"""Un test par règle objective restante.

Décision du 05/09/2026 : aucune règle Python ne touche plus au fond ni au style.
Les tests des règles supprimées sont partis avec elles ; ce fichier ne décrit que
ce qui reste, et le commentaire du module explique pourquoi si peu reste.
"""

from __future__ import annotations

import unittest

from app.linkedin_comments.controls import (
    ControlContext,
    check_detected_language_match,
    check_language_match,
    check_no_hyperlink,
    check_not_duplicate,
    detect_language,
    explain_violation,
    normalize_comment,
    run_controls,
)


class Hyperlink(unittest.TestCase):
    def test_url_is_refused(self):
        self.assertEqual(check_no_hyperlink("Voir https://exemple.com"), ["hyperlink_present"])

    def test_www_without_scheme_is_refused(self):
        self.assertEqual(check_no_hyperlink("Voir www.exemple.com"), ["hyperlink_present"])

    def test_plain_comment_passes(self):
        self.assertEqual(check_no_hyperlink("Une question sur votre méthode."), [])


class Language(unittest.TestCase):
    def test_declared_language_must_match(self):
        self.assertEqual(check_language_match("en", "fr"), ["language_mismatch"])
        self.assertEqual(check_language_match("fr", "fr"), [])

    def test_written_language_is_checked_too(self):
        """Un petit modèle peut déclarer fr et écrire en anglais."""
        self.assertEqual(
            check_detected_language_match("The method you describe is the one we use", "fr"),
            ["detected_language_mismatch"],
        )

    def test_ambiguous_text_does_not_fail(self):
        self.assertIsNone(detect_language("OK 2026"))
        self.assertEqual(check_detected_language_match("OK 2026", "fr"), [])


class Duplicate(unittest.TestCase):
    def test_same_comment_twice_is_refused(self):
        prior = frozenset({normalize_comment("Une question sur votre méthode.")})
        self.assertEqual(check_not_duplicate("une question sur votre methode", prior), [])
        self.assertEqual(check_not_duplicate("Une question sur votre méthode.", prior), ["duplicate_comment"])


class StyleIsNoLongerControlledByCode(unittest.TestCase):
    """Le fond et le style passent par les prompts et le juge, plus par du code.

    Ce test décrit une décision, pas un défaut : un commentaire long, plein de
    mots creux et portant un tiret cadratin ne déclenche plus aucune violation.
    C'est au juge de le renvoyer en réécriture.
    """

    def test_a_verbose_comment_full_of_filler_words_now_passes(self):
        ctx = ControlContext(
            comment=(
                "Cette approche me semble absolument essentielle et cruciale — elle est fondamentale pour "
                "comprendre les enjeux majeurs de la transformation, et il est important de noter qu'elle "
                "reste incontournable dans un monde où tout change très vite en permanence."
            ),
            declared_language="fr",
            expected_language="fr",
        )
        self.assertEqual(run_controls(ctx), [])


class ViolationExplanations(unittest.TestCase):
    def test_known_code_is_translated(self):
        self.assertIn("lien", explain_violation("hyperlink_present"))

    def test_unknown_code_returns_itself(self):
        self.assertEqual(explain_violation("code_inconnu"), "code_inconnu")


if __name__ == "__main__":
    unittest.main()
