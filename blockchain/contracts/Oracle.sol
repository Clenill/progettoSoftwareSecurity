//SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.28;

import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";

contract Oracle is AccessControl {
    using Math for uint256;

    enum EvidenceType {
        SYMPTOMS, 
        DEVICE_SIGNAL, 
        PRESCRIPTION, 
        CONFIRMATION, 
        GPS_SIGNAL
    }

    struct EvidenceInfo {
        EvidenceType evidence;
        uint256 ptrue;
        uint256 pfalse;
        bool active;
    }

    struct EvidenceStatus {
        EvidenceType evidence;
        bool active;
    }

    struct Visit {
        bytes16 id;
        bytes16 physician;
        bytes16 patient;
        bool active;
        uint256 posterior;
        EvidenceStatus[] evidences;
    }

    // attributes
    bytes32 public constant PERMISSIONED_ROLE = keccak256("PERMISSIONED_ROLE");
    address private _adminAccount;

    uint256 public scale;
    uint256 private _prior;
    EvidenceInfo[] private _likelihoods;
    Visit[] private _visits;

    mapping(EvidenceType => uint256) private _infoIds;
    mapping(bytes16 => uint256) private _visitIds;

    // events
    event VisitAdded(address indexed account, bytes16 author, bytes16 visit);
    event VisitEdited(address indexed account, bytes16 author, bytes16 visit);
    event VisitCancelled(address indexed account, bytes16 author, bytes16 visit);
    event EvidenceAdded(address indexed account, bytes16 author, bytes16 visit, EvidenceType evidence);
    event PriorSet(address indexed account);
    event LikelihoodSet(address indexed account, EvidenceType evidence);
    event LikelihoodRemoved(address indexed account, EvidenceType evidence);

    // errors
    error Unauthorized();
    error ZeroDivision();
    error VisitNotFound(bytes16 visit);
    error DuplicateVisit(bytes16 visit);
    error LikelihoodNotFound(EvidenceType evidence);
    error DuplicateLikelihood(EvidenceType evidence);
    error DuplicateEvidence(bytes16 visit, EvidenceType evidence);
    error InvalidScaleValue(uint256 value);
    error InvalidLikelihood(uint256 value);
    error InvalidPrior(uint256 value);

    // constructor
    constructor(
        address adminAccount, 
        uint256 scaleValue, 
        uint256 initialPrior, 
        uint256 initialTrueLikelihood, 
        uint256 initialFalseLikelihood
    ) {
        uint256 scaleCopy = scaleValue;
        while(scaleCopy > 1 && scaleCopy % 10 == 0) {
            scaleCopy /= 10;
        }

        if(scaleCopy != 1) {
            revert InvalidScaleValue(scaleValue);
        }

        if(initialTrueLikelihood > scaleValue) {
            revert InvalidLikelihood(initialTrueLikelihood);
        }

        if(initialFalseLikelihood > scaleValue) {
            revert InvalidLikelihood(initialFalseLikelihood);
        }

        if(initialPrior > scaleValue) {
            revert InvalidPrior(initialPrior);
        }

        scale = scaleValue;
        _visits.push();
        _likelihoods.push();
        _prior = initialPrior;
        _adminAccount = adminAccount;
        _grantRole(DEFAULT_ADMIN_ROLE, _adminAccount);
        _grantRole(PERMISSIONED_ROLE, _adminAccount);

        EvidenceInfo memory tmp;
        tmp.ptrue = initialTrueLikelihood;
        tmp.pfalse = initialFalseLikelihood;
        tmp.active = true;

        uint256 evidenceTypeMax = uint256(type(EvidenceType).max);
        for(uint256 evidenceType = 0; evidenceType < evidenceTypeMax + 1; ++evidenceType) {
            tmp.evidence = EvidenceType(evidenceType);
            setLikelihood(tmp);
        }
    }

    // modifiers
    modifier isPermissioned() {
        if(!hasRole(PERMISSIONED_ROLE, msg.sender)) {
            revert Unauthorized();
        }
        _;
    }

    modifier isAdmin() {
        if(!hasRole(DEFAULT_ADMIN_ROLE, msg.sender)) {
            revert Unauthorized();
        }
        _;
    }

    modifier visitExists(bytes16 id) {
        uint256 index = _visitIds[id];
        if(index == 0) {
            revert VisitNotFound(id);
        }
        _;
    }

    modifier newVisit(bytes16 id) {
        uint256 index = _visitIds[id];
        if(index != 0) {
            revert DuplicateVisit(id);
        }
        _;
    }

    modifier likelihoodExists(EvidenceType evidence) {
        uint256 index = _infoIds[evidence];
        if(index == 0 || !_likelihoods[index].active) {
            revert LikelihoodNotFound(evidence);
        }
        _;
    }

    // functions
    function _getPosterior(Visit memory visit) internal view returns (uint256) {
        uint256 ptrue = _prior;
        uint256 pfalse = scale - _prior;

        for(uint256 i = 0; i < visit.evidences.length; ++i) {
            uint256 index = _infoIds[visit.evidences[i].evidence];
            if(index != 0 && _likelihoods[index].active) {
                if(visit.evidences[i].active) {
                    ptrue = Math.mulDiv(ptrue, _likelihoods[index].ptrue, scale);
                    pfalse = Math.mulDiv(pfalse, _likelihoods[index].pfalse, scale);
                }

                else {
                    ptrue = Math.mulDiv(ptrue, scale - _likelihoods[index].ptrue, scale);
                    pfalse = Math.mulDiv(pfalse, scale - _likelihoods[index].pfalse, scale);
                }
            }
        }

        (bool success, uint256 value) = Math.tryDiv(ptrue * scale, ptrue + pfalse);
        if(!success) {
            revert ZeroDivision();
        }

        return value;
    }

    function addPermissionedAccount(address account) external {
        _grantRole(DEFAULT_ADMIN_ROLE, account);
        grantRole(PERMISSIONED_ROLE, account);
    }

    function removePermissionedAccount(address account) external {
        if(account == _adminAccount) {
            revert Unauthorized();
        }

        _revokeRole(DEFAULT_ADMIN_ROLE, account);
        revokeRole(PERMISSIONED_ROLE, account);
    }

    function getFactPrior() external view isPermissioned returns (uint256) {
        return _prior;
    }

    function setFactPrior(uint256 value) external isAdmin {
        if(value > scale) {
            revert InvalidPrior(value);
        }

        _prior = value;
        emit PriorSet(msg.sender);
    }

    function getLikelihood(EvidenceType evidence) external view isPermissioned likelihoodExists(evidence) returns (EvidenceInfo memory) {
        return _likelihoods[_infoIds[evidence]];
    }

    function setLikelihood(EvidenceInfo memory info) public isPermissioned {
        if(info.ptrue > scale) {
            revert InvalidLikelihood(info.ptrue);
        }

        if(info.pfalse > scale) {
            revert InvalidLikelihood(info.pfalse);
        }

        uint256 index = _infoIds[info.evidence];
        info.active = true;
        if(index == 0) {
            _likelihoods.push(info);
            _infoIds[info.evidence] = _likelihoods.length - 1;
        }

        else {
            _likelihoods[index] = info;
        }

        emit LikelihoodSet(msg.sender, info.evidence);
    }

    function removeLikelihood(EvidenceType evidence) external isPermissioned likelihoodExists(evidence) {
        _likelihoods[_infoIds[evidence]].active = false;
        emit LikelihoodRemoved(msg.sender, evidence);
    }

    function getLikelihoods() external view isPermissioned returns (EvidenceInfo[] memory) {
        uint256 length = 0;
        for(uint256 i = 1; i < _likelihoods.length; ++i) {
            if(_likelihoods[i].active) {
                ++length;
            }
        }

        uint256 j = 0;
        EvidenceInfo[] memory likelihoods = new EvidenceInfo[](length);
        for(uint256 i = 1; i < _likelihoods.length; ++i) {
            if(_likelihoods[i].active) {
                likelihoods[j] = _likelihoods[i];
                ++j;
            }
        }

        return likelihoods;
    }

    function getVisit(bytes16 id) external view isPermissioned visitExists(id) returns (Visit memory) {
        Visit memory visit = _visits[_visitIds[id]];
        visit.posterior = _getPosterior(visit);
        return visit;
    }

    function getVisitCount() external view isPermissioned returns (uint256) {
        return _visits.length - 1;
    }

    function getVisits(bytes16[] calldata ids) external view isPermissioned returns (Visit[] memory) {
        uint256 length = 0;
        for(uint256 i = 0; i < ids.length; ++i) {
            if(_visitIds[ids[i]] != 0) {
                ++length;
            }
        }

        Visit[] memory visits = new Visit[](length);
        uint256 j = 0;
        for(uint256 i = 0; i < ids.length; ++i) {
            uint256 index = _visitIds[ids[i]];
            if(index != 0) {
                visits[j] = _visits[index];
                visits[j].posterior = _getPosterior(visits[j]);
                ++j;
            }
        }

        return visits;
    }

    function getVisitsPaged(uint256 offset, uint256 size) external view isPermissioned returns (Visit[] memory) {
        uint256 length = _visits.length - 1;
        if(offset > length) {
            return new Visit[](0);
        }

        if(offset + size > length) {
            size = length - offset;
        }

        Visit[] memory visits = new Visit[](size);
        for(uint256 i = 0; i < size; ++i) {
            visits[i] = _visits[offset + i + 1];
            visits[i].posterior = _getPosterior(visits[i]);
        }

        return visits;
    }

    function addVisit(bytes16 author, bytes16 id, bytes16 physician, bytes16 patient) external isPermissioned newVisit(id) {
        _visits.push();
        uint256 index = _visits.length - 1;
        _visitIds[id] = index;

        Visit storage visit = _visits[index];
        visit.physician = physician;
        visit.patient = patient;
        visit.id = id;
        visit.active = true;
        emit VisitAdded(msg.sender, author, id);
    }

    function cancelVisit(bytes16 author, bytes16 id) external isPermissioned visitExists(id) {
        _visits[_visitIds[id]].active = false;
        emit VisitCancelled(msg.sender, author, id);
    }

    function editVisit(bytes16 author, bytes16 id, bytes16 physician, bytes16 patient) external isPermissioned visitExists(id) {
        Visit storage visit = _visits[_visitIds[id]];
        visit.physician = physician;
        visit.patient = patient;
        emit VisitEdited(msg.sender, author, id);
    }

    function addEvidence(bytes16 author, bytes16 id, EvidenceType evidence, bool value) external isPermissioned visitExists(id) {
        Visit storage visit = _visits[_visitIds[id]];
        for(uint256 i = 0; i < visit.evidences.length; ++i) {
            if(evidence == visit.evidences[i].evidence) {
                revert DuplicateEvidence(id, evidence);
            }
        }

        visit.evidences.push(EvidenceStatus(evidence, value));
        emit EvidenceAdded(msg.sender, author, id, evidence);
    }
}

