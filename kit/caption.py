"""Build the Instagram caption and first comment from content.json.

Usage: python3 kit/caption.py content.json OUT_DIR
Writes OUT_DIR/caption.txt and OUT_DIR/comment.txt. Exit code 2 if either is
over Instagram's 2,200-character limit or has more than 30 hashtags.

The text under the post carries the whole written content of the carnet,
copied word for word: caption = hook, the 6 numbers, the 90-second pitch
(French version), the day's appointments, disclaimer, hashtags; first comment =
the three headlines with their effect, then the geopolitical topic.
No emoji.
"""
import json, pathlib, sys

LIMIT = 2200
STEP_FR = ["Le marché ce matin", "Les deux mouvements", "Pourquoi", "Ce que ça change", "Ce qu'on surveille"]


def main():
    C = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    k, post = C["carnet"], C["post"]

    six = "\n".join(f"{x['label']} : {x['niveau']} ({x['variation']})" for x in k["six"])
    pitch = "\n\n".join(f"{STEP_FR[i] if i < len(STEP_FR) else s['etape']} : {s['fr']}" for i, s in enumerate(k["pitch"]))
    rdv = post.get("rendez_vous_court") or k["heure_impact"]
    caption = (
        f"{post['hook']}\n\n"
        f"LES 6 CHIFFRES (clôtures de {post.get('jour_cloture', 'la veille')})\n{six}\n\n"
        f"LE PITCH EN 90 SECONDES\n{pitch}\n\n"
        f"RENDEZ-VOUS DU JOUR\n{rdv}\n\n"
        "Les trois titres économiques et la géopolitique sont en commentaire.\n"
        "Information générale, pas un conseil en investissement.\n\n"
        f"{post['hashtags']}"
    )
    titres = "\n\n".join(f"{i}. {t['titre']} {t['contexte']}\nEffet pour un client ou un produit structuré : {t['effet']}"
                         for i, t in enumerate(k["titres"], 1))
    comment = f"TROIS TITRES ÉCONOMIQUES\n\n{titres}\n\nGÉOPOLITIQUE\n{k['geopolitique']}"

    (out / "caption.txt").write_text(caption, encoding="utf-8")
    (out / "comment.txt").write_text(comment, encoding="utf-8")
    tags = post["hashtags"].count("#")
    report = {"caption_chars": len(caption), "comment_chars": len(comment), "hashtags": tags, "limit": LIMIT}
    errors = []
    if len(caption) > LIMIT:
        errors.append(f"caption too long by {len(caption) - LIMIT}: shorten post.rendez_vous_court or post.hook")
    if len(comment) > LIMIT:
        errors.append(f"comment too long by {len(comment) - LIMIT}: tighten the geopolitique or contexte wording in the carnet")
    if tags > 30:
        errors.append("more than 30 hashtags")
    report["errors"] = errors
    print(json.dumps(report, ensure_ascii=False))
    sys.exit(2 if errors else 0)


if __name__ == "__main__":
    main()
