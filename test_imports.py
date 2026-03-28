import sys
import os

sys.path.insert(0, os.getcwd())

try:
    from core.researcher import Researcher

    print("[OK] Researcher imported")
except Exception as e:
    print("[FAIL] Researcher import failed: {e}")

try:
    from core.alchemist import Alchemist

    print("[OK] Alchemist imported")
except Exception as e:
    print("[FAIL] Alchemist import failed: {e}")

try:
    from core.database import Database

    print("[OK] Database imported")
except Exception as e:
    print("[FAIL] Database import failed: {e}")

try:
    from core.architect import Architect

    print("[OK] Architect imported")
except Exception as e:
    print("[FAIL] Architect import failed: {e}")

try:
    from core.visual_director import VisualDirector

    print("[OK] VisualDirector imported")
except Exception as e:
    print("[FAIL] VisualDirector import failed: {e}")

try:
    from core.voice_director import VoiceDirector

    print("[OK] VoiceDirector imported")
except Exception as e:
    print("[FAIL] VoiceDirector import failed: {e}")

try:
    from core.logger import iniciar_registro_combate

    print("[OK] logger imported")
except Exception as e:
    print("[FAIL] logger import failed: {e}")

try:
    from core.clusterizador import ClusterizadorDolores

    print("[OK] ClusterizadorDolores imported")
except Exception as e:
    print("[FAIL] ClusterizadorDolores import failed: {e}")

try:
    from core.tendencias import RadarTendencia

    print("[OK] RadarTendencia imported")
except Exception as e:
    print("[FAIL] RadarTendencia import failed: {e}")

try:
    from core.extractor_frases import ExtractorFrases

    print("[OK] ExtractorFrases imported")
except Exception as e:
    print("[FAIL] ExtractorFrases import failed: {e}")

print("Import test completed.")
