import os
from mido import MidiFile, MidiTrack, Message

# Map MIDI note numbers to note names (ignoring octaves)
MIDI_NOTE_TO_NAME = {
    0: 'C', 1: 'c', 2: 'D', 3: 'd', 4: 'E', 5: 'F', 6: 'f', 7: 'G', 8: 'g', 9: 'A', 10: 'a', 11: 'B'
}

DEFAULT_DURATION = 500  # Default duration in milliseconds for invalid or negative timings

# Function to convert MIDI file to text sequence
def midi_to_text_sequence(midi_path):
    midi = MidiFile(midi_path)
    sequence = []
    last_event_time = 0  # Keeps track of time since the last event
    
    for track in midi.tracks:
        for msg in track:
            if msg.type == 'note_on' and msg.velocity > 0:  # Note starts
                note = MIDI_NOTE_TO_NAME.get(msg.note % 12, '')  # Map to note name
                octave = msg.note // 12  # Calculate octave
                if note:
                    # Time since the last event
                    rest_duration = max(msg.time - last_event_time, 0)  # Ensure non-negative
                    sequence.append((f"{note}{octave}", rest_duration))
                    last_event_time = msg.time

            elif msg.type == 'note_off':  # Increment time during note-off
                last_event_time += msg.time  # Increment rest time
    
    return sequence

# Function to convert text sequence back to MIDI
def text_sequence_to_midi(sequence, output_path):
    midi = MidiFile()
    track = MidiTrack()
    midi.tracks.append(track)
    
    for note_with_octave, duration in sequence:
        # Ensure non-negative time
        duration = max(duration, DEFAULT_DURATION)  # Set default duration if negative
        
        if note_with_octave == 'R':  # Handle rests
            track.append(Message('note_off', note=0, velocity=0, time=duration))
        else:
            base_note = note_with_octave[:-1]  # Extract the note (e.g., "C")
            octave = int(note_with_octave[-1])  # Extract the octave (e.g., "4")
            midi_note = list(MIDI_NOTE_TO_NAME.keys())[list(MIDI_NOTE_TO_NAME.values()).index(base_note)] + 12 * octave
            track.append(Message('note_on', note=midi_note, velocity=64, time=0))
            track.append(Message('note_off', note=midi_note, velocity=64, time=duration))
    
    midi.save(output_path)

# Directory containing the MIDI files
midi_dir = 'musicDatasetOriginal'

# Directory to store the resulting MIDI files
output_dir = 'musicDatasetSimplified'

# Create the output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    
# List to store the text sequences
text_sequences = []

# Process each MIDI file in the directory
for file_name in os.listdir(midi_dir):
    if file_name.endswith('.mid'):
        midi_path = os.path.join(midi_dir, file_name)
        text_sequence = midi_to_text_sequence(midi_path)
        if text_sequence:  # Check if the sequence is not empty
            text_sequences.append(text_sequence)
        else:
            print(f"No notes found in {file_name}")  # Debugging output

# Write the text sequences to a file
with open("inputMelodies.txt", "w") as file:
    for sequence in text_sequences:
        sequence_str = ' '.join([f"{note}:{duration}" for note, duration in sequence])
        file.write(sequence_str + "\n")

# Convert text sequences back to MIDI files
for i, sequence in enumerate(text_sequences):
    output_path = os.path.join(output_dir, f"output_midi_{i+1}.mid")
    text_sequence_to_midi(sequence, output_path)
    
print("Text sequences have been written to inputMelodies.txt")
