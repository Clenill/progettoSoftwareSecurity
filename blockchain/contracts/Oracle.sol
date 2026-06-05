//SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.28;

import "hardhat/console.sol";
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

    struct Visit {
        bytes16 physician;
        bytes16 patient;
        EvidenceType[] evidences;
        bool active;
    }

    // attributes
    bytes32 public constant PERMISSIONED_ROLE = keccak256("PERMISSIONED_ROLE");

    uint256 public scale;
    uint256 private _prior;
    EvidenceInfo[] private _likelihoods;
    mapping(EvidenceType => uint256) private _typeIds;
    Visit[] private _visits;
    mapping(bytes16 => uint256) private _visitIds;

    // events
    event PermissionedAccountAdded(address indexed account);
    event PermissionedAccountRemoved(address indexed account);
    event VisitAdded(address indexed account, bytes16 author, bytes16 visit);
    event VisitEdited(address indexed account, bytes16 author, bytes16 visit);
    event VisitCancelled(address indexed account, bytes16 author, bytes16 visit);
    event EvidenceAdded(address indexed account, bytes16 author, bytes16 visit, EvidenceType evidence);
    event PriorSet(address indexed account);
    event LikelihoodSet(address indexed account, EvidenceType evidence);
    event LikelihoodRemoved(address indexed account, EvidenceType evidence);

    // errors
    error VisitNotFound(bytes16 visit);
    error DuplicateVisit(bytes16 visit);
    error LikelihoodNotFound(EvidenceType evidence);
    error DuplicateLikelihood(EvidenceType evidence);
    error DuplicateEvidence(EvidenceType evidence);
    error Unauthorized();
    error ZeroDivision(uint256 numerator, uint256 denominator);

    // constructor
    constructor(address admin_account, uint256 scale_value) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin_account);
        _grantRole(PERMISSIONED_ROLE, admin_account);
        // lists should have an empty first element; nonexistent keys always get mapped to index 0
        _visits.push();
        _likelihoods.push();
        scale = scale_value;
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
        if(index == 0 || !_visits[index].active) {
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
        uint256 index = _typeIds[evidence];
        if(index == 0 || !_likelihoods[index].active) {
            revert LikelihoodNotFound(evidence);
        }
        _;
    }

    // functions
    function _getPosterior(Visit memory visit) internal view returns (uint256) {
        uint256 ptrue = _prior;
        uint256 pfalse = scale - _prior;

        // formula:
        // P(V|E1,...) = (P(V)*P(E1|V)*...)/[(P(V)*P(E1|V)*...) + (P(~V)*P(~E1|V)*...)]

        // for each evidence, update ptrue and pfalse with the likelihoods
        for(uint256 i = 0; i < visit.evidences.length; ++i) {
            EvidenceType _type = visit.evidences[i];
            uint256 index = _typeIds[_type];
            if(index == 0 || !_likelihoods[index].active) {
                revert LikelihoodNotFound(_type);
            }

            ptrue = Math.mulDiv(ptrue, _likelihoods[index].ptrue, scale);
            pfalse = Math.mulDiv(pfalse, scale - _likelihoods[index].ptrue, scale);
        }

        (bool success, uint256 posterior) = Math.tryDiv(ptrue * scale, ptrue + pfalse);
        if(!success) {
            revert ZeroDivision(ptrue, ptrue + pfalse);
        }

        return posterior;
    }

    function addPermissionedAccount(address account) public {
        _grantRole(DEFAULT_ADMIN_ROLE, account);
        grantRole(PERMISSIONED_ROLE, account);
        emit PermissionedAccountAdded(account);
    }

    function removePermissionedAccount(address account) public {
        if(account == msg.sender) {
            revert Unauthorized();
        }

        _revokeRole(DEFAULT_ADMIN_ROLE, account);
        revokeRole(PERMISSIONED_ROLE, account);
        emit PermissionedAccountRemoved(account);
    }

    function getFactPrior() public view isPermissioned returns (uint256) {
        return _prior;
    }

    function setFactPrior(uint256 value) public isAdmin {
        _prior = value;
        emit PriorSet(msg.sender);
    }

    function getLikelihood(EvidenceType evidence) public view isPermissioned likelihoodExists(evidence) returns (EvidenceInfo memory) {
        return _likelihoods[_typeIds[evidence]];
    }

    function setLikelihood(EvidenceInfo memory info) public isPermissioned {
        uint256 index = _typeIds[info.evidence];
        info.active = true;
        if(index == 0) {
            _likelihoods.push(info);
            _typeIds[info.evidence] = _likelihoods.length - 1;
        }

        else {
            _likelihoods[index] = info;
        }

        emit LikelihoodSet(msg.sender, info.evidence);
    }

    function removeLikelihood(EvidenceType evidence) public isPermissioned likelihoodExists(evidence) {
        _likelihoods[_typeIds[evidence]].active = false;
        emit LikelihoodRemoved(msg.sender, evidence);
    }

    function getLikelihoods() public view isPermissioned returns (EvidenceInfo[] memory) {
        return _likelihoods;
    }

    function getVisit(bytes16 id) public view isPermissioned visitExists(id) returns (Visit memory, uint256) {
        Visit storage visit = _visits[_visitIds[id]];
        return (visit, _getPosterior(visit));
    }

    function getVisits() public view isPermissioned returns (Visit[] memory, uint256[] memory) {
        uint256[] memory posteriors = new uint256[](_visits.length - 1);
        Visit[] memory visits = new Visit[](_visits.length - 1);
        for(uint256 i = 0; i < _visits.length - 1; ++i) {
            visits[i] = _visits[i+1];
            posteriors[i] = _getPosterior(_visits[i+1]);
        }

        return (visits, posteriors);
    }

    function addVisit(bytes16 author, bytes16 id, bytes16 physician, bytes16 patient) public isPermissioned newVisit(id) {
        Visit memory visit;
        visit.physician = physician;
        visit.patient = patient;
        visit.active = true;
        _visits.push(visit);
        _visitIds[id] = _visits.length - 1;
        emit VisitAdded(msg.sender, author, id);
    }

    function cancelVisit(bytes16 author, bytes16 id) public isPermissioned visitExists(id) {
        _visits[_visitIds[id]].active = false;
        emit VisitCancelled(msg.sender, author, id);
    }

    function editVisit(bytes16 author, bytes16 id, bytes16 physician, bytes16 patient) public isPermissioned visitExists(id) {
        Visit storage visit = _visits[_visitIds[id]];
        visit.physician = physician;
        visit.patient = patient;
        emit VisitEdited(msg.sender, author, id);
    }

    function addEvidence(bytes16 author, bytes16 id, EvidenceType evidence) public isPermissioned visitExists(id) {
        Visit storage visit = _visits[_visitIds[id]];
        for(uint256 i = 0; i < visit.evidences.length; ++i) {
            if(evidence == visit.evidences[i]) {
                revert DuplicateEvidence(evidence);
            }
        }

        visit.evidences.push(evidence);
        emit EvidenceAdded(msg.sender, author, id, evidence);
    }
}

