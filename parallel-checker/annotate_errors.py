from music21 import (converter,
                     interval,
                     note,
                     stream,
                     expressions,
                     layout,
                     style
                    )

def annotate(score):
    parts = score.parts
    if len(parts) < 2:
        print("Less than two parts in the score.")
        return score

    upper = parts[0].recurse().notesAndRests.stream()
    lower = parts[1].recurse().notesAndRests.stream()

    upper_notes = [n for n in upper if isinstance(n, note.Note)]
    lower_notes = [n for n in lower if isinstance(n, note.Note)]

    pairs = []
    for up_note in upper_notes:
        for low_note in lower_notes:
            if abs(up_note.offset - low_note.offset) < 0.01:
                pairs.append((up_note, low_note))
                break

    for i in range(len(pairs) - 1):
        n1u, n1l = pairs[i]
        n2u, n2l = pairs[i + 1]

        intvl1 = interval.Interval(n1l, n1u)
        intvl2 = interval.Interval(n2l, n2u)

        def mark_note(n, color, text):
            n.style.color       = color
            expr                = expressions.TextExpression(text)
            expr.style.fontSize = 8
            n.expressions.append(expr)

        if intvl1.simpleName == 'P5' and intvl2.simpleName == 'P5':
            mark_note(n1u, 'red', '|| 5th ||')
            mark_note(n2u, 'red', '|| 5th ||')

        if intvl1.simpleName == 'P8' and intvl2.simpleName == 'P8':
            mark_note(n1u, 'red', '|| 8ve ||')
            mark_note(n2u, 'red', '|| 8ve ||')

        if intvl2.simpleName == 'P5' and n1u.pitch != n2u.pitch and n1l.pitch != n2l.pitch:
            if (n2u.pitch.ps - n1u.pitch.ps) * (n2l.pitch.ps - n1l.pitch.ps) > 0:
                mark_note(n2u, 'orange', 'hidden 5th')

        if intvl2.simpleName == 'P8' and n1u.pitch != n2u.pitch and n1l.pitch != n2l.pitch:
            if (n2u.pitch.ps - n1u.pitch.ps) * (n2l.pitch.ps - n1l.pitch.ps) > 0:
                mark_note(n2u, 'orange', 'hidden 8ve')

    return score

score           = converter.parse("homework.musicxml")
annotated_score = annotate(score)
annotated_score.show()
# call LilyPond
annotated_score.write('lily.pdf', fp = 'annotated.pdf')
