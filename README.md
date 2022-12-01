# Image Failure Injection

This code collects some tools to inject image failures and tries
to simplify the usage for dataset injection.

The work is based on:
- https://github.com/AndreaCeccarelli/Python_Image_Failures
- https://github.com/UjjwalSaxena/Automold--Road-Augmentation-Library

The _InjectionManager_ takes as an input a folder with a sequence of frames 
(_png images_) and injects the selected failures. The output is a folder 
(named as the initial sequence) with a subfolder for every injection. 
Every failure could have multiple variants, therefore inside the 
failure output folder a new subfolder is created for every variant.
Every failure variant folder contains the initial sequence with the injected failure.

Example:

- input
  - sequence_01
    - frame_01.png
    - frame_02.png
    - ...

If we inject "banding" and "condensation" failures the output 
would be:


- output
  - sequence_01
    - banding
      - variant_0
        - frame_01.png
        - frame_02.png
        - ...
      - variant_1
        - frame_01.png
        - frame_02.png
        - ...
    - condensation
      - variant_0
        - ...

