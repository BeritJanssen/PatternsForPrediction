import music21 as m21
import csv
import math
from fractions import Fraction


def parse_midi(midipiece):
    piece = m21.converter.parse(midipiece)
    return piece


def convert_to_mono(piece):
    mono = next((part for part in piece.parts if not [p for p in part.recurse().notes if len(p.pitches) > 1]), None)
    return mono


def convert_piece(piece, filename):
    convert_to_csv(piece, filename, write=True)
    convert_to_lisp(piece, filename)


def convert_to_csv(piece, filename=None):
    ''' given a piece parsed by music21, return a list of {'onset', 'pitch'} dictionaries
    optionally write out this data format as csv if filename is specified
    '''
    monophonic_csv = []
    collect_csv = []
    # monophonic = convert_to_mono(piece)
    # if monophonic:
    #     for event in monophonic.flat.notes:
    #         monophonic_csv.append({
    #             'onset': round(float(event.offset), 2),
    #             'pitch': event.pitch.midi
    #         })
    #     if filename:
    #         with open(filename+'_mono.csv', "w+") as f:
    #             writer = csv.DictWriter(f, fieldnames=monophonic_csv[0].keys())
    #             writer.writeheader()
    #             writer.writerows(monophonic_csv)
    for event in piece.flat.notes:
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
    if filename:
        with open(filename+'_poly.csv', "w+") as f:
            writer = csv.DictWriter(f, fieldnames=polyphonic_csv[0].keys())
            writer.writeheader()
            writer.writerows(polyphonic_csv)
    return monophonic_csv, polyphonic_csv


def convert_to_lisp(piece, filename):
    monophonic_lisp = []
    collect_lisp = []
    monophonic = convert_to_mono(piece)
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
    for voice, part in enumerate(piece.parts):
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