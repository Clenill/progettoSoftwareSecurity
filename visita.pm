dtmc

module GestioneVisite

    // s: stato della visita
    // 0 = CREATA (Non confermata)
    // 1 = CONFERMATA
    // 2 = IN_CORSO (Raccolta Prove / Evidence)
    // 3 = COMPLETATA (Successo)
    // 4 = CANCELLATA (Abortita prima della conferma)
    // 5 = FALLITA (No-show, scaduta o errore)
    s : [0..5] init 0;

    // --- STATO 0: CREATA ---
    // Può essere confermata (70%), cancellata dall'utente/admin (20%) o scadere/fallire (10%)
    [] s=0 -> 0.7 : (s'=1) + 0.2 : (s'=4) + 0.1 : (s'=5);

    // --- STATO 1: CONFERMATA ---
    // Non può più essere cancellata. Passa all'esecuzione (90%) o fallisce per no-show (10%)
    [] s=1 -> 0.9 : (s'=2) + 0.1 : (s'=5);

    // --- STATO 2: IN CORSO (Aggiunta Evidence/Prove) ---
    // Il medico inserisce sintomi/prescrizioni. 
    // Ha successo e si completa (95%), oppure si interrompe per problemi (5%)
    [] s=2 -> 0.95 : (s'=3) + 0.05 : (s'=5);

    // --- STATI ASSORBENTI (Terminali) ---
    [] s=3 -> 1.0 : (s'=3); // Completata
    [] s=4 -> 1.0 : (s'=4); // Cancellata
    [] s=5 -> 1.0 : (s'=5); // Fallita

endmodule

// Etichette utili per le proprietà PCTL
label "confermata" = s=1;
label "completata" = s=3;
label "cancellata" = s=4;
label "fallita"    = s=5;