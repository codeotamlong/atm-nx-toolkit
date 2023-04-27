# ATMOSPHERE-NX-TOOLKIT

Automatically build SD Card for Atmosphere-NX, Homebrew, Overlay menu, cheat codes, .etc

## Description

Because life is too short to do it manually!

- [x] SD Setup: Auto download and unpack Atmosphere-NX and other stuff (Based on https://rentry.org/SwitchHackingIsEasy)
   - [x] EmuNAND / SysNAND
   - [x] Verify after build

- [x] Firmware download (Credit: [darthsternie.net](https://darthsternie.net/switch-firmwares/))
- [x] Atmosphere-NX Utilities
   - [x] Change boot-logo (Credit: [friedkeenan](https://github.com/friedkeenan/switch-logo-patcher))
   - [x] Change splash-screen (Credit: [Atmosphere-NX](https://github.com/Atmosphere-NX/Atmosphere))

- [Cheat codes manager]
   - [x] Download cheat codes from [GBATemp](https://gbatemp.net/download/cheat-codes-sxos-and-ams-main-cheat-file-updated.36311/)
   - [x] Find cheat codes based on game's Name and Title ID
   - [x] Batch cheat codes copy to sdcard based on text file

## Getting Started

### Dependencies

* Python 3 (on Windows 10+, MacOS,...)
* Unpack .rar on MacOS might need some extra install

### Installing

```sh
git clone https://github.com/codeotamlong/atmosphere-nx-toolkit
cd atmosphere-nx-toolkit
pip install -r requirements.txt
```

### Executing program

```sh
python main.py

```

## Help

* Can not unrar on MacOS: May be need to install `unrar`

```sh
brew install rar
```

## Screenshot

### Auto-setup SD Card

![Auto-setup SD Card](/docs/auto-setup-sdcard.png)

### Download Firmware

![Download Firmware](/docs/download-fw-from-darthsternie.png)

### Batch cheat-codes copy

![Batch cheat-codes copy](/docs/batch-copy-cheatcodes.png)

### More screenshots at [/docs/](/docs/)

## Authors

It's me

## License

This project is licensed under the MIT License - see the LICENSE.md file for details

## Acknowledgments

* [https://rentry.org/SwitchHackingIsEasy](https://rentry.org/SwitchHackingIsEasy)
* [Atmosphere-NX](https://github.com/Atmosphere-NX/Atmosphere)
* [GBATemp](https://gbatemp.net/forums/nintendo-switch.283/)
* [Tinfoil.io](https://tinfoil.io/Download)
* [RARLab](https://www.rarlab.com/rar_add.htm)
* [kennethreitz-archive](https://github.com/kennethreitz-archive/clint/)
* [friedkeenan](https://github.com/friedkeenan/switch-logo-patcher)
* [rarfile](https://github.com/markokr/rarfile)
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
* GeeksForGeeks, StackOverFlow,...
