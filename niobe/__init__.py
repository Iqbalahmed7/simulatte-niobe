"""Niobe — PopScale-native study orchestration layer.

Niobe is the consumer-facing interface for PopScale-based research studies.
It sits above PopScale the way Morpheus sits above the Persona Generator:

    NiobeStudyRequest
         ↓
    run_niobe_study()       (Niobe)
         ↓
    run_study()             (PopScale study runner)
         ↓
    run_calibrated_generation() + run_population_scenario() + generate_report()
         ↓
    PersonaRecord cohort + SimulationResult + PopScaleReport

The four Simulatte building blocks:
    Persona Generator → PopScale → Morpheus / Niobe
"""
