image_extensions = [
    '.jpg',
    '.jpeg',
    '.png',
    '.gif',
    '.bmp',
    '.tiff',
    '.tif',
    '.webp',
    '.svg',
    '.ico',
    '.heic',
    '.heif',
    '.raw',
    '.cr2',  # Canon RAW
    '.nef',  # Nikon RAW
    '.arw',  # Sony RAW
    '.dng',  # Adobe Digital Negative
    '.orf',  # Olympus RAW
    '.rw2',  # Panasonic RAW
    '.psd',  # Photoshop
    '.ai',  # Adobe Illustrator
    '.eps',  # Encapsulated PostScript
    '.indd',  # Adobe InDesign
    '.jfif',
    '.avif',
    '.apng',
]
document_extensions = [
    '.pdf',
    '.doc',
    '.docx',
    '.txt',
    '.rtf',
    '.odt',  # OpenDocument Text
    '.tex',  # LaTeX
    '.wpd',  # WordPerfect
    '.pages',  # Apple Pages
    '.xls',
    '.xlsx',
    '.xlsm',
    '.ods',  # OpenDocument Spreadsheet
    '.numbers',  # Apple Numbers
    '.csv',
    '.tsv',
    '.ppt',
    '.pptx',
    '.pptm',
    '.odp',  # OpenDocument Presentation
    '.key',  # Apple Keynote
    '.md',  # Markdown
    '.rst',  # reStructuredText
    '.epub',
    '.mobi',
    '.azw',  # Amazon Kindle
    '.djvu',
    '.xps',
    '.oxps',
]
audio_extensions = [
    '.mp3',
    '.wav',
    '.flac',
    '.aac',
    '.ogg',
    '.oga',
    '.wma',
    '.m4a',
    '.aiff',
    '.aif',
    '.ape',
    '.alac',
    '.opus',
    '.wv',  # WavPack
    '.tta',  # True Audio
    '.dsd',
    '.pcm',
    '.amr',
    '.au',
    '.mid',
    '.midi',
    '.ra',  # RealAudio
    '.rm',  # RealMedia
    '.3gp',  # 3GPP (audio)
    '.mka',  # Matroska Audio
]
video_extensions = [
    '.mp4',
    '.avi',
    '.mkv',
    '.mov',
    '.wmv',
    '.flv',
    '.webm',
    '.m4v',
    '.mpg',
    '.mpeg',
    '.3gp',
    '.3g2',
    '.mxf',
    '.roq',
    '.nsv',
    '.f4v',
    '.f4p',
    '.f4a',
    '.f4b',
    '.ogv',  # Ogg Video
    '.vob',  # DVD Video
    '.gifv',
    '.qt',  # QuickTime
    '.yuv',
    '.rm',  # RealMedia Video
    '.rmvb',
    '.asf',
    '.amv',
    '.m2v',
    '.svi',
    '.divx',
    '.ts',  # MPEG Transport Stream
    '.m2ts',
    '.mts',
]
archive_extensions = [
    '.zip',
    '.rar',
    '.7z',
    '.tar',
    '.gz',
    '.bz2',
    '.xz',
    '.tgz',  # tar.gz
    '.tbz',  # tar.bz2
    '.tbz2',
    '.tar.gz',
    '.tar.bz2',
    '.tar.xz',
    '.iso',
    '.dmg',  # macOS Disk Image
    '.pkg',
    '.deb',  # Debian Package
    '.rpm',  # Red Hat Package
    '.cab',  # Windows Cabinet
    '.msi',  # Windows Installer
    '.jar',  # Java Archive
    '.war',  # Web Application Archive
    '.ear',  # Enterprise Archive
    '.apk',  # Android Package
    '.z',
    '.lz',
    '.lzma',
    '.zipx',
]
code_extensions = [
    '.py',
    '.js',
    '.jsx',
    '.ts',
    '.tsx',
    '.java',
    '.c',
    '.cpp',
    '.cc',
    '.cxx',
    '.h',
    '.hpp',
    '.cs',  # C#
    '.go',
    '.rs',  # Rust
    '.rb',  # Ruby
    '.php',
    '.swift',
    '.kt',  # Kotlin
    '.kts',
    '.m',  # Objective-C
    '.mm',
    '.scala',
    '.r',
    '.R',
    '.pl',  # Perl
    '.sh',
    '.bash',
    '.zsh',
    '.fish',
    '.ps1',  # PowerShell
    '.bat',
    '.cmd',
    '.vbs',
    '.lua',
    '.sql',
    '.html',
    '.htm',
    '.css',
    '.scss',
    '.sass',
    '.less',
    '.xml',
    '.json',
    '.yaml',
    '.yml',
    '.toml',
    '.ini',
    '.cfg',
    '.conf',
]
executable_extensions = [
    '.exe',
    '.app',  # macOS Application
    '.dmg',  # macOS Disk Image (also in archives)
    '.deb',  # Debian Package (also in archives)
    '.rpm',  # Red Hat Package (also in archives)
    '.msi',  # Windows Installer (also in archives)
    '.apk',  # Android Package (also in archives)
    '.bin',
    '.run',
    '.sh',  # Shell script (also in code)
    '.bat',  # Batch file (also in code)
    '.cmd',  # Command script (also in code)
    '.com',
    '.gadget',
    '.jar',  # Java (also in archives)
]
font_extensions = [
    '.ttf',  # TrueType Font
    '.otf',  # OpenType Font
    '.woff',
    '.woff2',
    '.eot',
    '.fon',
    '.fnt',
    '.pfb',  # PostScript Font Binary
    '.pfm',  # PostScript Font Metrics
]
database_extensions = [
    '.db',
    '.sqlite',
    '.sqlite3',
    '.mdb',  # Microsoft Access
    '.accdb',
    '.dbf',
    '.sdf',
    '.frm',  # MySQL
    '.myd',
    '.myi',
    '.ibd',
]
model_3d_extensions = [
    '.obj',
    '.fbx',
    '.dae',  # Collada
    '.3ds',
    '.blend',  # Blender
    '.stl',
    '.ply',
    '.gltf',
    '.glb',
    '.usd',
    '.usdz',
    '.ma',  # Maya ASCII
    '.mb',  # Maya Binary
    '.max',  # 3ds Max
    '.c4d',  # Cinema 4D
    '.skp',  # SketchUp
]
cad_extensions = [
    '.dwg',  # AutoCAD
    '.dxf',  # AutoCAD Exchange
    '.dgn',  # MicroStation
    '.rvt',  # Revit
    '.ifc',  # Industry Foundation Classes
    '.stp',  # STEP
    '.step',
    '.iges',
    '.igs',
    '.sat',  # ACIS
    '.sldprt',  # SolidWorks Part
    '.sldasm',  # SolidWorks Assembly
]
ebook_extensions = [
    '.epub',
    '.mobi',
    '.azw',
    '.azw3',
    '.fb2',
    '.lit',
    '.prc',
    '.lrf',
    '.tcr',
    '.pdb',  # Palm Database
]
system_extensions = [
    '.sys',
    '.dll',
    '.so',  # Shared Object (Linux)
    '.dylib',  # Dynamic Library (macOS)
    '.log',
    '.tmp',
    '.temp',
    '.bak',
    '.old',
    '.cache',
    '.lock',
    '.pid',
    '.dat',
    '.bin',
]
web_extensions = [
    '.html',
    '.htm',
    '.css',
    '.js',
    '.php',
    '.asp',
    '.aspx',
    '.jsp',
    '.json',
    '.xml',
    '.rss',
    '.atom',
    '.wasm',
    '.map',  # Source map
]

print(hash('Hello'))
print(hash('Hello'))
print(hash('Hello'))
print(hash('Hello'))