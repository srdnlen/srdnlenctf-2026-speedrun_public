# HomeMade


<table>
  <tr><th align="left">CTF</th><td>Srdnlen CyberCamp Speedrun 2026</td></tr>
  <tr><th align="left">Category</th><td>Misc</td></tr>
  <tr><th align="left">Author</th><td><a href="https://github.com/NicoXVI">@NicoXVI</a> (Nicola Ghisu)</td></tr>
</table>

---

## Description
```
Hey, Hacker! We've intercepted this communication and need your help
https://homemade.challs.srdnlen.it/?channel=1

Act fast — this won't last long!
```

## Overview
The link opens a mail thread between Alice and Bob, with a `fragments.zip` attachment in the comments:

```bash
$ unzip -l fragments.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
     1584  2026-10-23 17:38   j6azQTbO.png
     1064  2026-10-23 17:38   jJyvmqux.png
      856  2026-10-23 17:38   jLgYOv80.png
...
```

There are 48 `.png` files with random names, and none of them opens as an image.

### How the challenge works
Reading the conversation gives us everything we need:
1. Alice made her own "homemade" cipher. She XORs the file 8 bytes at a time with a key: `[block] XOR [KEY] = [encrypted_block]`;
2. she sent the encrypted files in `fragments.zip`;
3. she won't send the key on "This channel" (the page is opened with `?channel=1`);
4. she forgot to put the files back in order, and tells Bob to "look at what the *meta* tells you".

## Exploitation
So the solve has three steps: 
1. find the key 
2. decrypt the fragments
3. order flag pieces

### Solve
```
       fragments.zip
             │
           unzip 
             ▼
        extracted/        [48 encrypted PNGs]
             │
      XOR with the key    [key = b"iloveyou"]
             ▼
        decrypted/        [valid PNGs but shuffled]
             │
       read metadata      [Position: N]
             ▼
          pieces/         [image_1.png ... image_48.png]
             │
       Tesseract OCR      
             ▼
           flag
```

### Step 1 > Finding the key
Alice doesn't send the key on channel 1, so we try another one. Changing the URL to `?channel=2` opens a private message:

```
Hey Bob, here is the key...
key = b'iloveyou'
...hope no one is listening right now
```

> This could also be found by simply using PNG Magic Bytes: Every PNG starts with the same 8-byte signature `89 50 4E 47 0D 0A 1A 0A`, and the key is 8 bytes too, so XORing the first block of any fragment with the signature gives the whole key:
> ```py
> PNG_MAGIC = bytes.fromhex("89504e470d0a1a0a")
> key = xor(data[:8], PNG_MAGIC)  # b'iloveyou'
> ```

### Step 2 > Decrypting the fragments
XOR is its own inverse, so to decrypt we XOR each file again with the same key, repeated over the whole length:

```python
KEY = b"iloveyou"

def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b * (len(a) // len(b) + 1)))

for img in images:
    with open(f"{input_dir}/{img}", "rb") as image:
        plaintext = xor(image.read(), KEY)
    with open(f"{output_dir}/{img}", "wb") as out:
        out.write(plaintext)
```
Now the files open, and each one contains a single character of the flag. The names are random, though, so we don't know the order.

### Step 3 > Ordering the fragments
This is where the "meta" hint comes in, it refers to `metadata`.

Running `exiftool` on a decrypted image shows a custom metadata field called `Position`:

```bash
$ exiftool decrypted/j6azQTbO.png | grep Position
Position: 13
```

We read that value for every image and save it as `image_<position>.png`:

```python
def find(image_path, keyword):
    proc = subprocess.Popen(['exiftool', image_path], stdout=subprocess.PIPE)
    for line in proc.stdout.read().decode().splitlines():
        if keyword in line:
            return int(line.split(':')[-1])

number = find(image_path, "Position")
Image.open(image_path).save(f"pieces/image_{number}.png")
```

### Step 4 > Reading the flag
With 48 images you can just open them in order and copy the characters by hand. To save time, I used Tesseract in single-character mode (`--psm 10`) with a whitelist of the flag charset:

```python
result = subprocess.run(
    ["tesseract", str(image_path), "stdout", "--psm", "10",
     "-c", "tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ"
           "abcdefghijklmnopqrstuvwxyz0123456789_{}"],
    check=True, capture_output=True, text=True,
)
```

## Flag
And this gives me the flag:

```
srdnlen{d0_you_r3m3mber_h0w_t0_c0de_w1thout_AI?}
```
