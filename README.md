# Celeratas

The Latin Programming Language

![Tests](https://github.com/planto73/Celeratas/actions/workflows/tests.yml/badge.svg)
![Last Commit](https://img.shields.io/github/last-commit/planto73/Celeratas)
![Version](https://img.shields.io/github/v/release/planto73/Celeratas)

## Description

Built from python, Celeratas uses a custom ident-oriented syntax that features latin keywords. Although some of the text is written in latin, there is an English help menu with translations for all of the keywords.

## Getting Started

### Dependencies

-   Windows, Macos, Unix, or Linux
-   Python3

### Installing

-   Open the terminal and type:

```
pip3 install Celeratas
```

### Executing program

-   In order to open the Celeratas interactive shell, type the following into the terminal:

```
celer
```

-   From there, you can type 'auxilium' (meaning help) to learn about the basics of the language.

```
auxilium
```

-   If you want to read from a file instead, add the file name as an argument.

```
celer file_you_want_to_read.clr
```

## Author

Finn Mattis

## Version History

-   1.0.0

    -   The initial release of Celeratas! Integers, Floats, Roman Numerals, Bools, Strings, Arrays, Hash Maps, Variables, Conditionals, Loops, Try-excepts, Functions, and more!

-   1.1.0

    -   Added support for assigning multiple variables at a time. Ex:

    ```
    a, b = val1, val2
    ```

    -   Can now access basic dunders from python import

-   1.1.1

    -   Hotfix for python import dunders not working
    -   Updated Readme and Grammar rules

-   1.2.0

    -   Can now access the shell with 'celer'
    -   Added keyword arguments to functions
    -   TONS of backend changes and better tests

-   1.2.1

    -   Added versioneer and started working on CI/CD

-   1.2.2

    -   Added automatic github actions to create a release and publish to pypi

-   1.3.0

    -   Can now read arguments with "\_\_args\_\_" variable
    -   Added split function for strings
    -   Improved help menu
    -   Fixed a LOT of bugs

## License

This project is licensed under the MIT License - see the LICENSE file for details
