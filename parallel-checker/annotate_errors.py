from music21 import (converter,
                     interval,
                     note,
                     stream,
                     expressions,
                     layout,
                     style
                    )
import pandas as pd
import itertools

score           = converter.parse("homework.musicxml")
parts           = score.parts

voice_names = []
for i, part in enumerate(parts):
    name = part.partName if part.partName else f'V{i+1}'
    voice_names.append(name)

def get_note_pairs(parts):
    all_notes  = [p.recurse().notes for p in parts]
    min_length = min(len(n)         for n in all_notes)
    pairs      = []

    for i in range(min_length - 1):
        current_notes = [n[i]     for n in all_notes]
        next_notes    = [n[i + 1] for n in all_notes]
        offset        = current_notes[0].offset

        for v1, v2 in itertools.combinations(range(len(all_notes)), 2):
            pairs.append({
                'voices' : (voice_names[v1], voice_names[v2]),
                'n1'     : current_notes[v1],
                'n2'     : current_notes[v2],
                'n1_next': next_notes[v1],
                'n2_next': next_notes[v2],
                'offset' : offset
            })
    return pairs

def annotate(pairs):
    error_list = []

    def is_hidden(prev_n1, prev_n2, next_n1, next_n2, target_interval):
        return (
            interval.Interval(next_n2, next_n1).simpleName == target_interval and
            prev_n1.nameWithOctave != next_n1.nameWithOctave and
            prev_n2.nameWithOctave != next_n2.nameWithOctave and
            (next_n1.pitch.ps - prev_n1.pitch.ps) * (next_n2.pitch.ps - prev_n2.pitch.ps) > 0
            )

    for pair in pairs:
        n1, n2   = pair['n1'],      pair['n2']
        n1n, n2n = pair['n1_next'], pair['n2_next']
        intvl1   = interval.Interval(n2 , n1 ).simpleName
        intvl2   = interval.Interval(n2n, n1n).simpleName

        def mark(note_obj, text, color):
            note_obj.style.color = color
            expr                 = expressions.TextExpression(text)
            expr.style.fontSize  = 8
            note_obj.expressions.append(expr)

        offset     = pair['offset']
        measure    = n1.measureNumber
        voice_pair = f"{pair['voices'][0]}-{pair['voices'][1]}"

        if intvl1 == 'P5' and intvl2 == 'P5':
            mark(n1,  '|| 5th ||', 'red')
            mark(n1n, '|| 5th ||', 'red')
            error_list.append((measure, offset, voice_pair, 'Parallel 5th', n1.nameWithOctave, n1n.nameWithOctave))

        elif intvl1 == 'P8' and intvl2 == 'P8':
            mark(n1,  '|| 8ve ||', 'red')
            mark(n1n, '|| 8ve ||', 'red')
            error_list.append((measure, offset, voice_pair, 'Parallel 8ve', n1.nameWithOctave, n1n.nameWithOctave))

        elif is_hidden(n1, n2, n1n, n2n, 'P5'):
            mark(n1n, 'hidden 5th', 'orange')
            error_list.append((measure, offset, voice_pair, 'Hidden 5th',  n1n.nameWithOctave, n2n.nameWithOctave))

        elif is_hidden(n1, n2, n1n, n2n, 'P8'):
            mark(n1n, 'hidden 8ve', 'orange')
            error_list.append((measure, offset, voice_pair, 'Hidden 8ve',  n1n.nameWithOctave, n2n.nameWithOctave))

    return error_list

note_pairs      = get_note_pairs(parts)
errors          = annotate(note_pairs)
score.show()
# call LilyPond
score.write('lily.pdf', fp = 'annotated.pdf')

df = pd.DataFrame(errors, columns = ['Measure', 'Offset', 'Voice Pair', 'Error Type', 'Note 1', 'Note 2'])
df.to_csv('analysis.csv', index = False, encoding = 'utf-8-sig')
