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

    struct Visit {
        bytes16 physician;
        bytes16 patient;
        EvidenceType[] evidences;
        bool active;
    }

    // attributes
    bytes32 public constant VALIDATOR_ROLE = keccak256("VALIDATOR_ROLE");

    uint256 public scale;
    uint256 private _prior;
    EvidenceInfo[] private _likelihoods;
    mapping(EvidenceType => uint256) private _typeIds;
    Visit[] private _visits;
    mapping(bytes16 => uint256) private _visitIds;

    // events
    event ValidatorAdded(address indexed validator);
    event ValidatorRemoved(address indexed validator);
    event VisitAdded(address indexed validator, bytes16 author, bytes16 visit);
    event VisitEdited(address indexed validator, bytes16 author, bytes16 visit);
    event VisitCancelled(address indexed validator, bytes16 author, bytes16 visit);
    event EvidenceAdded(address indexed validator, bytes16 author, bytes16 visit, EvidenceType evidence);
    event PriorSet(address indexed validator);
    event LikelihoodSet(address indexed validator, EvidenceType evidence);
    event LikelihoodRemoved(address indexed validator, EvidenceType evidence);

    // errors
    error VisitNotFound(bytes16 visit);
    error DuplicateVisit(bytes16 visit);
    error LikelihoodNotFound(EvidenceType evidence);
    error DuplicateLikelihood(EvidenceType evidence);
    error DuplicateEvidence(EvidenceType evidence);
    error Unauthorized();
    error ZeroDivision(uint256 numerator, uint256 denominator);

    // constructor
    constructor(address admin) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(VALIDATOR_ROLE, admin);
        // lists should have an empty first element; nonexistent keys always get mapped to index 0
        _visits.push();
        _likelihoods.push();
    }

    // modifiers
    modifier isValidator() {
        if(!hasRole(VALIDATOR_ROLE, msg.sender)) {
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
            pfalse = Math.mulDiv(pfalse, _likelihoods[index].pfalse, scale);
        }

        (bool success, uint256 posterior) = Math.tryDiv(ptrue * scale, ptrue + pfalse);
        if(!success) {
            revert ZeroDivision(ptrue, ptrue + pfalse);
        }

        return posterior;
    }

    function addValidator(address validator) public {
        _grantRole(DEFAULT_ADMIN_ROLE, validator);
        grantRole(VALIDATOR_ROLE, validator);
        emit ValidatorAdded(validator);
    }

    function removeValidator(address validator) public {
        if(validator == msg.sender) {
            revert Unauthorized();
        }

        _revokeRole(DEFAULT_ADMIN_ROLE, validator);
        revokeRole(VALIDATOR_ROLE, validator);
        emit ValidatorRemoved(validator);
    }

    function getFactPrior() public view isValidator returns (uint256) {
        return _prior;
    }

    function setFactPrior(uint256 value) public isAdmin {
        _prior = value;
        emit PriorSet(msg.sender);
    }

    function getLikelihood(EvidenceType evidence) public view isValidator likelihoodExists(evidence) returns (EvidenceInfo memory) {
        return _likelihoods[_typeIds[evidence]];
    }

    function setLikelihood(EvidenceInfo memory info) public isAdmin {
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

    function removeLikelihood(EvidenceType evidence) public isAdmin likelihoodExists(evidence) {
        _likelihoods[_typeIds[evidence]].active = false;
        emit LikelihoodRemoved(msg.sender, evidence);
    }

    function getLikelihoods() public view isValidator returns (EvidenceInfo[] memory) {
        return _likelihoods;
    }

    function getVisit(bytes16 id) public view isValidator visitExists(id) returns (Visit memory, uint256) {
        Visit storage visit = _visits[_visitIds[id]];
        return (visit, _getPosterior(visit));
    }

    function addVisit(bytes16 author, bytes16 id, bytes16 physician, bytes16 patient) public isValidator newVisit(id) {
        Visit memory visit;
        visit.physician = physician;
        visit.patient = patient;
        _visits.push(visit);
        _visitIds[id] = _visits.length - 1;
        emit VisitAdded(msg.sender, author, id);
    }

    function cancelVisit(bytes16 author, bytes16 id) public isValidator visitExists(id) {
        _visits[_visitIds[id]].active = false;
        emit VisitCancelled(msg.sender, author, id);
    }

    function editVisit(bytes16 author, bytes16 id, bytes16 physician, bytes16 patient) public isValidator visitExists(id) {
        Visit storage visit = _visits[_visitIds[id]];
        visit.physician = physician;
        visit.patient = patient;
        emit VisitEdited(msg.sender, author, id);
    }

    function addEvidence(bytes16 author, bytes16 id, EvidenceType evidence) public isValidator visitExists(id) {
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

