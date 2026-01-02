# TCGLiveUtils
Extracts data from Pokémon TCG Live's files downloaded in your machine and formats the content into csv, json or mediawiki-based tables.

## Setup

Steps 1-3 are not required to see avatar and gameplay content

1. Extract TCG Live's `DataTableCustomFormatter` class from `Managed\CardDatabase.DataAccess.dll` into the `TCGLiveBinaryExtractor` project, then compile it

5. Copy the `config-cache` folder from `%localappdata%low\pokemon\Pokemon TCG Live` into `TCGLiveBinaryExtractor`'s compiled project directory

3. Run `TCGLiveBinaryExtractor`, and copy the output folder to the parent folder if not already there

4. Install Python if you don't have it already

5. Copy the `config-cache` and `localization-cache` folders from `%localappdata%low\pokemon\Pokemon TCG Live` into the parent folder

6. Running the scripts into a terminal such as `python .\tcgliveladder.py` will create a default generated file

## Todo
- Typings
- Bypass DataTable extractor dependency
- Save outputs in a centralized folder
- Fix localization for specific langs

## Contributing
Feel free to submit a pull request to extract more diverse content or fix stuff.

## Special thanks
- eitentei for figuring the card database logic
