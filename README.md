# binsnitch
binsnitch can be used to detect silent unwanted changes to binaries on your system.
It will scan a given directory recursively for executable files and keep track of any changes it detects, based on the SHA256 hash of the file.

### Requirements
- python 3
- "file" command (available by default on unix systems)

### Running and usage
```
usage: binsnitch.py [-h] [-v] dir

positional arguments:
  dir            the directory to monitor

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  increase output verbosity
```

Example: monitor all files on the system and enable verbose logging

```
python3.5 binsnitch.py -v / 
```

### How it works
Once ``binsnitch.py`` is running, it will scan all files in ``dir`` (provided through a required command line argument) recursively, and create a SHA256 hash of each executable it finds. It then does the following:
- If a file is not known yet by ``binsnitch.py``, its details will be added to ``data/db.json`` (file name, file type and hash).
- If a file is already known but the calculated hash is different from the one in ``data/db.json``, an alert will be logged to ``data/alert.log``. In addition, the new hash will be added to the appropriate entry in ``data/db.json``.
- If a file is already known and the hash is identical to the one already in ``data/alert.log``, nothing happens.

### Example output

##### data/alerts.log
```
05/15/2017 02:46:17 AM - INFO - Scanning system for new and modified executable files, this can take a long time
05/15/2017 02:53:38 AM - INFO - Modified binary detected:/Applications/Cyberduck.app/Contents/Frameworks/Sparkle.framework/Versions/A/Resources/Autoupdate.app/Contents/MacOS/Autoupdate - new hash: a897613ab9ecd8ead7b697012036b2ef683a9df7afe99d9013e5dd6c3e08af10
05/15/2017 02:53:39 AM - INFO - Modified binary detected:/Applications/Cyberduck.app/Contents/Frameworks/Sparkle.framework/Versions/A/Resources/Autoupdate.app/Contents/MacOS/fileop - new hash: cdad8d7b1cce37547223a198e9fbbe256aed3919b58e1b2305870aeaac33c966
05/15/2017 02:53:41 AM - INFO - Modified binary detected:/Applications/Cyberduck.app/Contents/MacOS/Cyberduck - new hash: 3941de0b9001c616c6fcfdb76108fa5da46bdcdd3089e1feb65578c2d251eeec
```

##### data/db.json

```
[
    {
        "path": "/Applications/1Password 6.app/Contents/Frameworks/AgileLibrary.framework/Versions/A/Resources/pngquant",
        "sha256": [
            "47ecd7d9978a291de70aaf5e4392664d5c697cd0867bb59f3d6833671b83d448"
        ],
        "type": "Mach-O 64-bit executable x86_64"
    }
]
```

### Internals
Checking if a file is executable is done by launching a subprocess to the ``file`` command. If the output of this command contains the substring ``exe``, it will be processed by ``binsnitch.py``.

In its current version, ``binsnitch.py`` eats up a lot of CPU. This is caused by the recursive walk through the filesystem and the calculation of SHA256 hashes for each and every executable file it encounters.

### Ideas for improvement

- Include a switch for a single pass instead of running forever
- Remove dependency on ``file`` command to check for file type information
- Be nicer to system resources (IO and CPU)

### Why binsnitch?

Malware will often settle itself by overwriting existing executable applications in order to avoid detection.
Recent malware cases (May 2017) do this, including HandBrake being hacked to drop new variant of the Proton malware and the WannaCry ransomware overwriting ``C:\WINDOWS\system32\tasksche.exe``.
This triggered us to write a simple tool that could be used to detect this.

binsnitch can also be used during malware analysis, to detect silent changes to executable files (i.e. replacement of a trusted Windows executable by a trojaned version).

### References

Similar tools:
- Microsoft File Checksum Integrity Verifier - https://www.microsoft.com/en-us/download/details.aspx?id=11533
- Syscheck in OSSEC - http://ossec-docs.readthedocs.io/en/latest/manual/syscheck/

Both these tools are either OS-dependent or require installation of libraries / tools. 
``binsnitch.py`` aims at being dependent on ``python`` and ``file`` only.

### Community

Bug reports and feature requests are welcome in the issues tab!

Contact us: research@nviso.be.

binsnitch is developed and maintained by Daan Raman.

