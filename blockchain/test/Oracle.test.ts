
import path from "path";
import dotenv from "dotenv";
import crypto from "crypto";
import { expect } from "chai";
import { network } from "hardhat";
//import { ethers } from "hardhat";
//import networkHelpers, { loadFixture } from "@nomicfoundation/hardhat-toolbox-mocha-ethers/network-helpers";

dotenv.config({
    path: path.join(
        import.meta.dirname, '..', '..', '.env'
    )
});

const connection = await network.getOrCreate();
const ethers: any = connection.ethers;
const networkHelpers: any = connection.networkHelpers;
const loadFixture: any = networkHelpers.loadFixture;

describe("Oracle - Test delle funzioni", function() {
    let account: string;
    let _scale: number;
    let _initialPrior: number;
    let _initialTrueLikelihood: number;
    let _initialFalseLikelihood: number;
    let PERMISSIONED_ROLE: any;

    //let ethers: any;
    //let loadFixture: any;
    //let networkHelpers: any;

    before(async function() {
        //ethers = connection.ethers;
        //networkHelpers = connection.networkHelpers;
        //loadFixture = connection.networkHelpers.loadFixture;
        account = process.env.W3_ACCOUNT || '';
        _scale = parseInt(process.env.SCALE || '100000000');
        _initialPrior = Math.trunc(
            parseFloat(process.env.INITIAL_PRIOR || '0.5') * _scale
        );
        _initialTrueLikelihood = Math.trunc(
            parseFloat(process.env.INITIAL_TRUE_LIKELIHOOD || '0.5') * _scale
        );
        _initialFalseLikelihood = Math.trunc(
            parseFloat(process.env.INITIAL_FALSE_LIKELIHOOD || '0.5') * _scale
        );
        PERMISSIONED_ROLE = ethers.id("PERMISSIONED_ROLE");
    });


    // helpers
    function uuidToHex(uuid: string) {
        return "0x" + uuid.replace(/-/g, "");
    }

    function generateVisit() {
        let author = uuidToHex(crypto.randomUUID());
        return {
            author: author, 
            id: uuidToHex(crypto.randomUUID()), 
            physician: uuidToHex(crypto.randomUUID()), 
            patient: author
        };
    }

    async function deploy() {
        await networkHelpers.setNextBlockBaseFeePerGas(0);
        const signer = await ethers.getImpersonatedSigner(account);
        if(!signer) {
            throw new Error("Nessun account di deployment trovato");
        }

        const factory = await ethers.getContractFactory(process.env.CONTRACT_NAME || '');
        const contract = await factory.deploy(
            account, _scale, _initialPrior, _initialTrueLikelihood, _initialFalseLikelihood
        );

        await contract.waitForDeployment();
        return { contract, signer };
    }

    // TESTS
    describe("constructor()", function() {
        it("Dovrebbe effettuare il deployment con successo", 
            async function() {
                await loadFixture(deploy);
            }
        );

        it("Dovrebbe fallire se la scala è nulla", 
            async function() {
                const factory = await ethers.getContractFactory(process.env.CONTRACT_NAME || '');
                await expect(
                    factory.deploy(
                        account, 
                        0, 
                        _initialPrior, 
                        _initialTrueLikelihood, 
                        _initialFalseLikelihood
                    )
                ).to.revert(ethers);
            }
        );

        it("Dovrebbe fallire se la scala non è una potenza di 10", 
            async function() {
                const factory = await ethers.getContractFactory(process.env.CONTRACT_NAME || '');
                await expect(
                    factory.deploy(
                        account, 
                        200000000, 
                        _initialPrior, 
                        _initialTrueLikelihood, 
                        _initialFalseLikelihood
                    )
                ).to.revert(ethers);
            }
        );

        it("Dovrebbe fallire se la probabilità a priori iniziale è maggiore della scala", 
            async function() {
                const factory = await ethers.getContractFactory(process.env.CONTRACT_NAME || '');
                await expect(
                    factory.deploy(
                        account, 
                        _scale, 
                        _scale + 1, 
                        _initialTrueLikelihood, 
                        _initialFalseLikelihood
                    )
                ).to.revert(ethers);
            }
        )

        it("Dovrebbe fallire se la verosimiglianza (vera) iniziale è maggiore della scala", 
            async function() {
                const factory = await ethers.getContractFactory(process.env.CONTRACT_NAME || '');
                await expect(
                    factory.deploy(
                        account, 
                        _scale, 
                        _initialPrior, 
                        _scale + 1, 
                        _initialFalseLikelihood
                    )
                ).to.revert(ethers);
            }
        )

        it("Dovrebbe fallire se la verosimiglianza (falsa) iniziale è maggiore della scala", 
            async function() {
                const factory = await ethers.getContractFactory(process.env.CONTRACT_NAME || '');
                await expect(
                    factory.deploy(
                        account, 
                        _scale, 
                        _initialPrior, 
                        _initialTrueLikelihood, 
                        _scale + 1
                    )
                ).to.revert(ethers);
            }
        )
    });

    describe("addPermissionedAccount", function() {
        it("Dovrebbe aggiungere con successo i permessi ad un nuovo account", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                const newWallet = ethers.Wallet.createRandom();
                const newUser = await newWallet.connect(ethers.provider);
                await expect(contract.connect(signer)
                    .addPermissionedAccount(newUser.address)
                ).to.emit(contract, "RoleGranted");
            }
        );
    });

    describe("removePermissionedAccount", function() {
        it("Dovrebbe rimuovere con successo i permessi ad un account che li possiede", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                const newWallet = ethers.Wallet.createRandom();
                const newUser = await newWallet.connect(ethers.provider);
                await expect(contract.connect(signer)
                    .addPermissionedAccount(newUser.address)
                ).to.emit(contract, "RoleGranted");
                await expect(contract.connect(signer)
                    .removePermissionedAccount(newUser.address)
                ).to.emit(contract, "RoleRevoked");
            }
        );

        it("Dovrebbe fallire nel tentativo di rimuovere i permessi dell'account admin", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                await expect(contract.connect(signer)
                    .removePermissionedAccount(signer.address)
                ).to.revert(ethers);
            }
        );
    });

    describe("getFactPrior()", function() {
        it("Dovrebbe restituire la probabilità a priori predefinita", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                expect(await contract.connect(signer)
                    .getFactPrior()
                ).to.equal(_initialPrior);
            }
        );
    });

    describe("setFactPrior()", function() {
        it("Dovrebbe modificare la probabilità a priori", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                const newPrior = Math.trunc(Math.random() * _scale);
                await expect(contract.connect(signer)
                    .setFactPrior(newPrior)
                ).not.to.revert(ethers);
                expect(await contract.connect(signer)
                    .getFactPrior()
                ).to.equal(newPrior);
            }
        );

        it("Dovrebbe fallire nel tentativo di impostare una probabilità a priori maggiore di 1", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                await expect(contract.connect(signer)
                    .setFactPrior(_scale + 1)
                ).to.revert(ethers);
            }
        );

        it("Dovrebbe fallire se l'account chiamante non è admin", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                const newWallet = ethers.Wallet.createRandom();
                const newUser = await newWallet.connect(ethers.provider);
                await expect(contract.connect(newUser)
                    .setFactPrior(_initialPrior)
                ).to.revert(ethers);
            }
        );
    });

    describe("getLikelihood()", function() {
        it("Dovrebbe restituire le verosimiglianze predefinite delle prove", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                const likelihoods = await contract.connect(signer)
                    .getLikelihood(0);
                expect(likelihoods.ptrue).to.equal(_initialTrueLikelihood);
                expect(likelihoods.pfalse).to.equal(_initialFalseLikelihood);
            }
        );

        it("Dovrebbe fallire nel tentativo di ottenere le verosimiglianze di una prova inesistente", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                await expect(contract.connect(signer)
                    .removeLikelihood(0)
                ).to.emit(contract, "LikelihoodRemoved");
                await expect(contract.connect(signer)
                    .getLikelihood(0)
                ).to.revert(ethers);
            }
        );

        it("Dovrebbe fallire se l'account chiamante non ha i permessi", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                const newWallet = ethers.Wallet.createRandom();
                const newUser = await newWallet.connect(ethers.provider);
                await expect(contract.connect(newUser)
                    .getLikelihood(0)
                ).to.revert(ethers);
            }
        );
    });

    describe("setLikelihood()", function() {
        it("Dovrebbe modificare le verosimiglianze di una prova esistente", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                const newTrueLikelihood = Math.trunc(Math.random() * _scale);
                const newFalseLikelihood = Math.trunc(Math.random() * _scale);
                await expect(contract.connect(signer)
                    .setLikelihood({
                        evidence: 0, 
                        ptrue: newTrueLikelihood, 
                        pfalse: newFalseLikelihood, 
                        active: true
                    })
                ).not.to.revert(ethers);
            }
        );

        it("Dovrebbe fallire nell'inserimento di verosimiglianza true maggiori di 1", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                await expect(contract.connect(signer)
                    .setLikelihood({
                        evidence: 0, 
                        ptrue: _scale + 1, 
                        pfalse: _initialFalseLikelihood, 
                        active: true
                    })
                ).to.revert(ethers);
            }
        );

        it("Dovrebbe fallire nell'inserimento di verosimiglianza false maggiori di 1", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                await expect(contract.connect(signer)
                    .setLikelihood({
                        evidence: 0, 
                        ptrue: _initialTrueLikelihood, 
                        pfalse: _scale + 1, 
                        active: true
                    })
                ).to.revert(ethers);
            }
        );
    });

    describe("removeLikelihood()", function() {
        it("Dovrebbe rimuovere una verosimiglianza esistente", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                await expect(contract.connect(signer)
                    .removeLikelihood(0)
                ).not.to.revert(ethers);
            }
        );

        it("Dovrebbe fallire nel tentativo di rimozione di una verosimiglianza inesistente", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                await contract.connect(signer).removeLikelihood(0);
                await expect(contract.connect(signer)
                    .removeLikelihood(0)
                ).to.revert(ethers);
            }
        );
    });

    describe("getLikelihoods()", function() {
        it("Dovrebbe ottenere la lista delle verosimiglianze", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                const likelihoodsArray = await contract.connect(signer)
                    .getLikelihoods();
                expect(likelihoodsArray.every(
                    (L: any, i: number) => L.evidence === BigInt(i)
                )).to.be.true;
            }
        );
    });

    describe("getVisit()", function() {
        it("Dovrebbe restituire una visita presente", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                const visit = generateVisit();
                await expect(contract.connect(signer)
                    .addVisit(
                        visit.author, visit.id, visit.physician, visit.patient
                    )
                ).to.emit(contract, "VisitAdded");
                const outputVisit = await contract.connect(signer)
                    .getVisit(visit.id);
                expect({
                    id: outputVisit.id, 
                    physician: outputVisit.physician, 
                    patient: outputVisit.patient
                }).to.deep.equal({
                    id: visit.id, 
                    physician: visit.physician, 
                    patient: visit.patient
                });
            }
        );

        it("Dovrebbe fallire nella ricerca di una visita inesistente", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                const visit = generateVisit();
                await expect(contract.connect(signer)
                    .getVisit(visit.id)
                ).to.revert(ethers);
            }
        );
    });

    describe("addVisit()", function() {
        it("Dovrebbe inserire una nuova visita", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                const visit = generateVisit();
                await expect(contract.connect(signer)
                    .addVisit(
                        visit.author, visit.id, visit.physician, visit.patient
                    )
                ).not.to.revert(ethers);
            }
        );

        it("Dovrebbe fallire nell'inserimento di una visita già presente", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                const visit = generateVisit();
                await contract.connect(signer)
                    .addVisit(
                        visit.author, visit.id, visit.physician, visit.patient
                    );
                await expect(contract.connect(signer)
                    .addVisit(
                        visit.author, visit.id, visit.physician, visit.patient
                    )
                ).to.revert(ethers);
            }
        );
    });

    describe("editVisit", function() {
        it("Dovrebbe modificare una visita esistente", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                const visit = generateVisit();
                const newPhysician = generateVisit().physician;
                await contract.connect(signer)
                    .addVisit(
                        visit.author, visit.id, visit.physician, visit.patient
                    );
                await expect(contract.connect(signer)
                    .editVisit(
                        visit.author, visit.id, newPhysician, visit.patient
                    )
                ).not.to.revert(ethers);
            }
        );

        it("Dovrebbe fallire in caso di richiesta di modifica di una visita esistente", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                const visit = generateVisit();
                await expect(contract.connect(signer)
                    .editVisit(
                        visit.author, visit.id, visit.physician, visit.patient
                    )
                ).to.revert(ethers);
            }
        );
    });

    describe("cancelVisit()", function() {
        it("Dovrebbe annullare una visita esistente", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                const visit = generateVisit();
                await contract.connect(signer)
                    .addVisit(
                        visit.author, visit.id, visit.physician, visit.patient
                    );
                await expect(contract.connect(signer)
                    .cancelVisit(visit.author, visit.id)
                ).not.to.revert(ethers);
            }
        );

        it("Dovrebbe fallire in caso di richiesta di annullamento di una visita inesistente", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                const visit = generateVisit();
                await expect(contract.connect(signer)
                    .cancelVisit(visit.author, visit.id)
                ).to.revert(ethers);
            }
        );
    });

    describe("getVisitsPaged()", function() {
        it("Dovrebbe ritornare una lista di 0 elementi (nessuna visita)", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                expect(await contract.connect(signer)
                    .getVisitsPaged(0, 10)
                ).to.have.lengthOf(0);
            }
        );

        it("Dovrebbe ritornare una lista di 0 elementi (offset superiore alla dimensione)", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                const visits = [1,2,3].map((_: any) => generateVisit());
                for(let v of visits) {
                    await contract.connect(signer)
                        .addVisit(
                            v.author, v.id, v.physician, v.patient
                        );
                }
                expect(await contract.connect(signer)
                    .getVisitsPaged(4, 10)
                ).to.have.lengthOf(0);
            }
        );

        it("Dovrebbe ritornare una lista di 3 elementi", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                const visits = [1,2,3].map((_: any) => generateVisit());
                for(let v of visits) {
                    await contract.connect(signer)
                        .addVisit(
                            v.author, v.id, v.physician, v.patient
                        );
                }

                expect(await contract.connect(signer)
                    .getVisitsPaged(0, 10)
                ).to.have.lengthOf(3);
            }
        );
    });

    describe("getVisits()", function() {
        it("Dovrebbe ritornare una lista vuota", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                expect(await contract.connect(signer)
                    .getVisits([])
                ).to.have.lengthOf(0);
            }
        );

        it("Dovrebbe restituire una lista con un elemento", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                const visits = [1,2,3].map((_: any) => generateVisit());
                for(let v of visits) {
                    await contract.connect(signer)
                        .addVisit(
                            v.author, v.id, v.physician, v.patient
                        );
                }

                expect(await contract.connect(signer)
                    .getVisits([visits[0].id])
                ).to.have.lengthOf(1);
            }
        );
    });

    describe("getVisitCount()", function() {
        it("Dovrebbe ritornare 0", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                expect(await contract.connect(signer)
                    .getVisitCount()
                ).to.equal(0);
            }
        );

        it("Dovrebbe restituire 1", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                const visit = generateVisit();
                await contract.connect(signer)
                    .addVisit(
                        visit.author, visit.id, visit.physician, visit.patient
                    );
                expect(await contract.connect(signer)
                    .getVisitCount()
                ).to.equal(1);
            }
        );
    });

    describe("addEvidence()", function() {
        it("Dovrebbe aggiungere una nuova prova ad una visita esistente", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                const visit = generateVisit();
                await contract.connect(signer)
                    .addVisit(
                        visit.author, visit.id, visit.physician, visit.patient
                    );
                await expect(contract.connect(signer)
                    .addEvidence(
                        visit.author, visit.id, 0, true
                    )
                ).not.to.revert(ethers);
            }
        );

        it("Dovrebbe fallire nell'aggiunta di una prova già esistente", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                const visit = generateVisit();
                await contract.connect(signer)
                    .addVisit(
                        visit.author, visit.id, visit.physician, visit.patient
                    );
                await contract.connect(signer)
                    .addEvidence(
                        visit.author, visit.id, 0, true
                    );
                await expect(contract.connect(signer)
                    .addEvidence(
                        visit.author, visit.id, 0, true
                    )
                ).to.revert(ethers);
            }
        );

        it("Dovrebbe fallire nell'aggiunta di una prova ad una visita inesistente", 
            async function() {
                const { contract, signer } = await loadFixture(deploy);
                const visit = generateVisit();
                await expect(contract.connect(signer)
                    .addEvidence(
                        visit.author, visit.id, 0, true
                    )
                ).to.revert(ethers);
            }
        );
    });

    describe("_getPosterior()", function() {
        it("Dovrebbe fallire se le probabilità sono tutte nulle (per prova vera)", 
            async function() {
                const signer = await ethers.getImpersonatedSigner(account);
                const factory = await ethers.getContractFactory(process.env.CONTRACT_NAME || '');
                const contract = await factory.deploy(
                    account, 
                    _scale, 
                    0, 0, 0
                );

                await contract.waitForDeployment();

                const visit = generateVisit();
                await expect(contract.connect(signer)
                    .addVisit(
                        visit.author, visit.id, visit.physician, visit.patient
                    )
                ).to.emit(contract, "VisitAdded");

                await expect(contract.connect(signer)
                    .addEvidence(
                        visit.author, visit.id, 0, true
                    )
                ).to.emit(contract, "EvidenceAdded");

                await expect(contract.connect(signer)
                    .getVisit(visit.id)
                ).to.revert(ethers);
            }
        );

        it("Dovrebbe fallire se le probabilità sono tutte pari a 1 (per prova falsa)", 
            async function() {
                const signer = await ethers.getImpersonatedSigner(account);
                const factory = await ethers.getContractFactory(process.env.CONTRACT_NAME || '');
                const contract = await factory.deploy(
                    account, 
                    _scale, 
                    0, _scale, _scale
                );

                await contract.waitForDeployment();

                const visit = generateVisit();
                await expect(contract.connect(signer)
                    .addVisit(
                        visit.author, visit.id, visit.physician, visit.patient
                    )
                ).to.emit(contract, "VisitAdded");

                await expect(contract.connect(signer)
                    .addEvidence(
                        visit.author, visit.id, 0, false
                    )
                ).to.emit(contract, "EvidenceAdded");

                await expect(contract.connect(signer)
                    .getVisit(visit.id)
                ).to.revert(ethers);
            }
        );
    });
});

