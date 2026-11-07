CHORD RADIANCE — rudimentary TouchDesigner keyboard instrument
Built and checked in TouchDesigner 2023.12370 (macOS).

LOAD & PLAY
Drag ChordRadiance.tox into a TouchDesigner network. Right-click the
component and choose View, then click inside its viewer to focus it.
Keep the timeline playing. No external Python packages or assets required.

1 = C MAJOR layout
Keys:   A  S  D  F  G  H  J  K  L
Notes: C4 D4 E4 F4 G4 A4 B4 C5 D5
Example: hold A+D+G for C major; S+F+H for D minor.

2 = PIANO layout (white and black keys in chromatic pitch order)
Keys:   A  W   S  E   D  R  F   T  G   Y  J  U   I  K   O  L
Notes: C4 C#4 D4 D#4 E4 F4 F#4 G4 G#4 A4 A#4 B4 C5 C#5 D5 D#5
This follows the exact AWSEDRFTGYJUIKOL sequence requested, including R=F4.
Example: hold A+D+T for C major in this layout.

Hold multiple keys to play a chord. Release keys to stop each note.
SPACE or ESC = all notes off. Changing layouts also clears held notes.
The component's Instrument page offers Layout, Volume, and Audio Enabled.
Audio uses the system's default output. Keyboard input is scoped to this
component's focused viewer. If a note sticks after switching windows,
focus the viewer and press SPACE. Keyboard hardware may limit held keys.

COLORS & SOUND
C starts at red; pitch classes proceed around the HSV hue wheel in 12 steps.
Octaves share a color. Bottom swatches highlight held pitch classes.
Individual notes appear as colored satellites; the center radiates their
blended chord color with animated rings. Hue is averaged on a circle so
red/violet boundaries blend correctly. Equal weights per held pitch;
saturation=0.8 and value=1 for active chords. Perfect cancellation uses
the lowest held note's hue. This is a creative mapping, not a standard.
Recognizes major/minor/diminished/augmented/sus2/sus4/7/maj7/m7 shapes.
Other combinations display note names. Synth uses polyphonic sine voices
with a subtle second harmonic, attack/release envelopes and soft limiting.

FILES
ChordRadiance.tox  self-contained playable component
engine.py         readable source embedded in the TOX
color_map.json    12 pitch-class colors and HSV values
preview.png       C-major chord rendering
verification.json TouchDesigner signal, mapping, render and reload checks

VERIFIED
C4/E4/G4 mapping and C chord label; all 16 chromatic pitches; nonzero finite
stereo audio samples; 960x540 rendering; reload under a different name;
no reported operator errors. Physical speaker playback was not listened to.
