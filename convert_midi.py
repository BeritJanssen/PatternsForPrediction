import music21 as m21
import csv
import math
from fractions import Fraction


def parse_midi(midipiece):
    piece = m21.converter.parse(midipiece)
    qpiece = piece.quantize()
    filename = midipiece[:-4]
    return qpiece, filename


def convert_to_monophonic(qpiece):
    monophonic = next((part for part in qpiece if not [p for p in part.recurse().notes if len(p.pitches) > 1]), None)


def convert_piece(qpiece, filename):
    #parse_to_lisp(qpiece, filename)
    return parse_to_csv(qpiece, filename)


def parse_to_csv(qpiece, filename, write=False):
    monophonic_csv = []
    collect_csv = []
    convert_to_monophonic(qpiece)
    if monophonic:
        for event in monophonic.recurse().notes:
            monophonic_csv.append({
                'onset': round(float(event.offset), 2),
                'pitch': event.pitch.midi
            })
        if write:
            with open(filename+'_mono.csv', "w+") as f:
                writer = csv.DictWriter(f, fieldnames=monophonic_csv[0].keys())
                writer.writeheader()
                writer.writerows(monophonic_csv)
    for event in qpiece.recurse().notes:
        try:
            collect_csv.append({
                'onset': round(float(event.offset), 2), 
                'pitch': event.pitch.midi
            })
        except:
            # this event is a chord
            pitches = event.pitches
            for p in pitches:
                collect_csv.append({
                    'onset': round(float(event.offset), 2), 
                    'pitch': p.midi
                })
    polyphonic_csv = sorted(collect_csv, key=lambda k: k['onset'])
    if write:
        with open(filename+'_poly.csv', "w+") as f:
            writer = csv.DictWriter(f, fieldnames=polyphonic_csv[0].keys())
            writer.writeheader()
            writer.writerows(polyphonic_csv)
    return monophonic_csv, polyphonic_csv


def parse_to_lisp(qpiece, filename):
    monophonic_lisp = []
    collect_lisp = []
    monophonic = next((part for part in qpiece if not [p for p in part.recurse().notes if len(p.pitches) > 1]), None)
    # index, monophonic = next((
    #     index, part for index, part in enumerate(qpiece) if not 
    #     [p for p in part.recurse().notes if len(p.pitches) > 1]
    # ), None)
    if monophonic:
        for event in monophonic.recurse().notes:
            diatonic_pitch = diatonic_pitch_lookup[event.pitch.step] + math.floor(event.pitch.midi/12) * 7 - 12
            monophonic_lisp.append((
                str(Fraction(event.offset)),
                event.pitch.midi-21,
                diatonic_pitch,
                str(Fraction(event.quarterLength)),
                index))
        with open(filename+'_mono.txt', "w+") as f:
            for m_tuple in monophonic_lisp:
                f.write(str(m_tuple)+'\n')
    for voice, part in enumerate(qpiece):
        print(voice)
        for event in part.recurse().notes:
            try:
                diatonic_pitch = diatonic_pitch_lookup[event.pitch.step] + math.floor(event.pitch.midi/12) * 7 - 12
                collect_lisp.append((
                    str(Fraction(event.offset)), 
                    event.pitch.midi-21, 
                    diatonic_pitch, 
                    str(Fraction(event.quarterLength)), 
                    voice))
            except:
                # this event is a chord
                pitches = event.pitches
                for p in pitches:
                    diatonic_pitch = diatonic_pitch_lookup[p.step] + math.floor(p.midi/12) * 7 - 12
                    collect_lisp.append((
                        str(Fraction(event.offset)), 
                        p.midi - 21, 
                        diatonic_pitch, 
                        str(Fraction(event.quarterLength)), 
                        voice))
    polyphonic_lisp = sorted(collect_lisp, key=lambda k: k[0])
    with open(filename+'_poly.txt', "w+") as f:
        for p_tuple in polyphonic_lisp:
            f.write(str(p_tuple)+'\n')
    return monophonic_lisp, polyphonic_lisp


diatonic_pitch_lookup = {
    'C': 0,
    'D': 1,
    'E': 2,
    'F': 3,
    'G': 4,
    'A': 5,
    'B': 6
}