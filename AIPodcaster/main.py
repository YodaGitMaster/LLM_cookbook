

from transformers import BarkModel
import scipy.io.wavfile as wavfile
model = BarkModel.from_pretrained("suno/bark")

import torch
import scipy
from transformers import AutoProcessor
import os
import time
import glob
import numpy as np
import textwrap

device = "cuda:0" if torch.cuda.is_available() else "cpu"
model = model.to(device)
processor = AutoProcessor.from_pretrained("suno/bark")
# sampling_rate = model.generation_config.sample_rate
sampling_rate = 22050
voice_preset = "v2/en_speaker_6"

start_time = time.time()
text_prompt = """"""

with open("script.txt", "r", encoding="utf-8") as file:
    text_prompt = file.read()

# Split the text_prompt into chunks of length 250
chunk_size = 200
chunks = textwrap.wrap(text_prompt, chunk_size)
print(f"Total chunks to process {len(chunks)}")
# Create a directory to store the individual output files
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Loop through the input chunks
for i, chunk in enumerate(chunks, 1):
    # Process the chunk
    inputs = processor(chunk, voice_preset=voice_preset)
    speech_output = model.generate(**inputs.to(device))
    
    # Save the output as a WAV file
    output_filename = os.path.join(output_dir, f"output_{i}.wav")
    wavfile.write(output_filename, rate=sampling_rate, data=speech_output[0].cpu().numpy())
    
    print(f"Chunk {i} generated and saved as {output_filename}")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken: {elapsed_time:.2f} seconds")
    
    
# Get all the individual output files in the directory
output_files = glob.glob(os.path.join(output_dir, "output_*.wav"))

# Sort the files based on the numerical part of the file name
output_files.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))

# Combine all the output files into one
combined_output = np.concatenate([wavfile.read(file)[1] for file in output_files])

# Print each file as it is added to the concatenated output
for file in output_files:
    print("Adding file:", file)


# Save the combined output as a single WAV file
output_filename = os.path.join(output_dir, f"final_output.wav")
wavfile.write(output_filename, rate=sampling_rate, data=combined_output)



print(f"All chunks combined and saved as {output_filename}")
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Total time taken: {elapsed_time:.2f} seconds")
