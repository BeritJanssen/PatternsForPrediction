import music21 as m21
import csv


def parse_midi(midipiece):
    monophonic_output = []
    collect_output = []
    piece = m21.converter.parse(midipiece)
    qpiece = piece.quantize()
    monophonic = next((part for part in qpiece if not [p for p in part.recurse().notes if len(p.pitches) > 1]), None)
    if monophonic:
        for event in monophonic.recurse().notes:
            monophonic_output.append({'onset': event.offset, 'pitch': event.pitch.midi})
        with open(midipiece[:-4]+'_mono.csv', "w+") as f:
            writer = csv.DictWriter(f, fieldnames=monophonic_output[0].keys())
            writer.writeheader()
            writer.writerows(monophonic_output)
    for event in qpiece.recurse().notes:
        try:
            collect_output.append({'onset': event.offset, 'pitch': event.pitch.midi})
        except:
            # this event is a chord
            pitches = event.pitches
            for p in pitches:
                collect_output.append({'onset': event.offset, 'pitch': p.midi})
    polyphonic_output = sorted(collect_output, key=lambda k: k['onset'])
    with open(midipiece[:-4]+'_poly.csv', "w+") as f:
        writer = csv.DictWriter(f, fieldnames=polyphonic_output[0].keys())
        writer.writeheader()
        writer.writerows(polyphonic_output)
    return monophonic_output, polyphonic_output