# Documentation Update Process

## Current version: 1.46 (Update all instances of old version number with new one for commands below)

To update the documentation from one version to another:

1. Install required Python packages:

   ```bash
   pip install -r scripts/doc_merger/requirements.txt
   ```

> Assumes mdoc.exe is in your $PATH, likely located somewhere like: C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\MSBuild\Xamarin\Android\
> AND assumes $VS_INSTALL_PATH environment variables has been set. likely: C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional
> You may need to change some of the paths in the following command

1. Generate initial mdoc documentation from the datalogic-xamarin-sdk repository and place it into the generated-docs/mdoc folder:
   * mdoc update --lib="C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\ReferenceAssemblies\Microsoft\Framework\MonoAndroid\v9.0" --lib="C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Xamarin\Android" --lib="C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\ReferenceAssemblies\Microsoft\Framework\MonoAndroid\v1.0" -o generated-docs/mdoc ..\\datalogic-xamarin-sdk\\datalogic-xamarin-sdk\\bin\\Release\\datalogic-xamarin-sdk.dll

1. Get the stub code for the desired version of the SDK, which has Javadoc comments
   * MANUALLY DOWNLOAD AND UNZIP: [https://github.com/datalogic/datalogic-android-sdk/archive/v1.46.zip](https://github.com/datalogic/datalogic-android-sdk/archive/v1.46.zip)

1. Generate Javadocs and place into generated-docs/javadoc:
   * javadoc  --ignore-source-errors -sourcepath datalogic-android-sdk-1.46\sdk\src\main\java -subpackages com -notree -noindex -nohelp -nonavbar -d generated-docs\javadoc

1. Run the documentation merger:

   ```bash
   python scripts/doc_merger/run_merger.py --mdoc generated-docs/mdoc --javadoc generated-docs/javadoc --html html --output html --version 1.46
   ```

1. Verify the updated documentation in the output directory.

1. Replace the current HTML documentation with the updated version.
