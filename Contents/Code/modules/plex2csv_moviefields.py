##############################################################################
# Plex WebTools helper unit for ExportTools module
#
# Author: dane22, a Plex Community member
#
##############################################################################

# Fields that contains a timestamp and should return a date
dateTimeFields = ['addedAt', 'updatedAt', 'lastViewedAt']

# Fields that contains a timestamp and should return a time
timeFields = ['duration']

fields = {
    "Media ID": {
        "field": "@ratingKey",
        "ReqLevel": 1,
        "id": 1},
    "Title": {
        "field": "@title",
        "ReqLevel": 1,
        "id": 2},
    "Sort title": {
        "field": "@titleSort",
        "ReqLevel": 1,
        "id": 3},
    "Studio": {
        "field": "@studio",
        "ReqLevel": 1,
        "id": 4},
    "Content Rating": {
        "field": "@contentRating",
        "ReqLevel": 1,
        "id": 5},
    "Year": {
        "field": "@year",
        "ReqLevel": 1,
        "id": 6},
    "Rating": {
        "field": "@rating",
        "ReqLevel": 1,
        "id": 7},
    "Summary": {
        "field": "@summary",
        "ReqLevel": 1,
        "id": 8},
    "Genres": {
        "field": "Genre/@tag",
        "ReqLevel": 1,
        "id": 9},
    "View Count": {
        "field": "@viewCount",
        "ReqLevel": 1,
        "id": 10},
    "Last Viewed at": {
        "field": "@lastViewedAt",
        "ReqLevel": 1,
        "id": 11},
    "Tagline": {
        "field": "@tagline",
        "ReqLevel": 1,
        "id": 12},
    "Release Date": {
        "field": "@originallyAvailableAt",
        "ReqLevel": 1,
        "id": 13},
    "Writers": {
        "field": "Writer/@tag",
        "ReqLevel": 1,
        "id": 14},
    "Country": {
        "field": "Country/@tag", "ReqLevel": 1, "id": 15},
    "Duration": {
        "field": "@duration", "ReqLevel": 1, "id": 16},
    "Directors": {
        "field": "Director/@tag", "ReqLevel": 1, "id": 17},
    "Roles": {
        "field": "Role/@tag", "ReqLevel": 1, "id": 18},
    "IMDB Id": {
        "field": "@guid", "ReqLevel": 1, "id": 19},
    "Labels": {
        "fields": "Label/@tag", "ReqLevel": 2, "id": 20},
    "Locked Fields": {
        "field": "Field/@name", "ReqLevel": 2, "id": 21},
    "Extras": {
        "field": "Extras/@size", "ReqLevel": 2, "id": 22},
    "Collections": {
        "field": "Collection/@tag", "ReqLevel": 2, "id": 23},
    "Original Title": {
        "field": "@originalTitle",
        "ReqLevel": 2,
        "id": 24},
    "Added": {
        "field": "@addedAt",
        "ReqLevel": 2,
        "id": 25},
    "Updated": {
        "field": "@updatedAt",
        "ReqLevel": 2,
        "id": 26},
    "Audio Languages": {
        "field": "Media/Part/Stream[@streamType=2]/@languageCode",
        "ReqLevel": 2,
        "id": 27},
    "Audio Title": {
        "field": "Media/Part/Stream[@streamType=2]/@title",
        "ReqLevel": 2,
        "id": 28},
    "Subtitle Languages": {
        "field": "Media/Part/Stream[@streamType=3]/@languageCode",
        "ReqLevel": 2,
        "id": 29},
    "Subtitle Title": {
        "field": "Media/Part/Stream[@streamType=3]/@title",
        "ReqLevel": 2,
        "id": 30},
    "Subtitle Codec": {
        "field": "Media/Part/Stream[@streamType=3]/@codec",
        "ReqLevel": 2,
        "id": 31},
    "Accessible": {
        "field": "Media/Part/@accessible",
        "ReqLevel": 2,
        "id": 32},
    "Exists": {
        "field": "Media/Part/@exists",
        "ReqLevel": 2,
        "id": 33},
    "Video Resolution": {
        "field": "Media/@videoResolution",
        "ReqLevel": 2,
        "id": 34},
    "Bitrate": {"field": "Media/@bitrate", "ReqLevel": 2, "id": 35},
    "Width": {"field": "Media/@width", "ReqLevel": 2, "id": 36},
    "Height": {"field": "Media/@height", "ReqLevel": 2, "id": 37},
    "Aspect Ratio": {"field": "Media/@aspectRatio", "ReqLevel": 2, "id": 38},
    "Audio Channels": {
        "field": "Media/@audioChannels",
        "ReqLevel": 2,
        "id": 39},
    "Audio Codec": {
        "field": "Media/@audioCodec",
        "ReqLevel": 2,
        "id": 40},
    "Video Codec": {"field": "Media/@videoCodec", "ReqLevel": 2, "id": 41},
    "Container": {
        "field": "Media/@container",
        "ReqLevel": 2,
        "id": 42},
    "Video FrameRate": {
        "field": "Media/@videoFrameRate",
        "ReqLevel": 2,
        "id": 43},
    "Part File": {"field": "Media/Part/@file", "ReqLevel": 2, "id": 44},
    "Part Size": {"field": "Media/Part/@size", "ReqLevel": 2, "id": 45},
    "Part Indexed": {"field": "Media/Part/@indexes", "ReqLevel": 2, "id": 46},
    "Part Duration": {
        "field": "Media/Part/@duration",
        "ReqLevel": 2,
        "id": 47},
    "Part Container": {
        "field": "Media/Part/@container",
        "ReqLevel": 2,
        "id": 48},
    "Part Optimized for Streaming": {
        "field": "Media/Part/@optimizedForStreaming",
        "ReqLevel": 2,
        "id": 49},
    "Video Stream Title": {
        "field": "Media/Part/Stream[@streamType=1]/@title",
        "ReqLevel": 2,
        "id": 50},
    "Video Stream Default": {
        "field": "Media/Part/Stream[@streamType=1]/@default",
        "ReqLevel": 2,
        "id": 51},
    "Video Stream Index": {
        "field": "Media/Part/Stream[@streamType=1]/@index",
        "ReqLevel": 2,
        "id": 52},
    "Video Stream Pixel Format": {
        "field": "Media/Part/Stream[@streamType=1]/@pixelFormat",
        "ReqLevel": 2,
        "id": 53},
    "Video Stream Profile": {
        "field": "Media/Part/Stream[@streamType=1]/@profile",
        "ReqLevel": 2,
        "id": 54},
    "Video Stream Ref Frames": {
        "field": "Media/Part/Stream[@streamType=1]/@refFrames",
        "ReqLevel": 2,
        "id": 55},
    "Video Stream Scan Type": {
        "field": "Media/Part/Stream[@streamType=1]/@scanType",
        "ReqLevel": 2,
        "id": 56},
    "Video Stream Stream Identifier": {
        "field": "Media/Part/Stream[@streamType=1]/@streamIdentifier",
        "ReqLevel": 2,
        "id": 57},
    "Video Stream Width": {
        "field": "Media/Part/Stream[@streamType=1]/@width",
        "ReqLevel": 2,
        "id": 58},
    "Video Stream Pixel Aspect Ratio": {
        "field": "Media/Part/Stream[@streamType=1]/@pixelAspectRatio",
        "ReqLevel": 2,
        "id": 59},
    "Video Stream Height": {
        "field": "Media/Part/Stream[@streamType=1]/@height",
        "ReqLevel": 2,
        "id": 60},
    "Video Stream Has Scaling Matrix": {
        "field": "Media/Part/Stream[@streamType=1]/@hasScalingMatrix",
        "ReqLevel": 2,
        "id": 61},
    "Video Stream Frame Rate Mode": {
        "field": "Media/Part/Stream[@streamType=1]/@frameRateMode",
        "ReqLevel": 2,
        "id": 62},
    "Video Stream Frame Rate": {
        "field": "Media/Part/Stream[@streamType=1]/@frameRate",
        "ReqLevel": 2,
        "id": 63},
    "Video Stream Codec": {
        "field": "Media/Part/Stream[@streamType=1]/@codec",
        "ReqLevel": 2,
        "id": 64},
    "Video Stream Codec ID": {
        "field"  "Media/Part/Stream[@streamType=1]/@codecID",
        "ReqLevel": 2,
        "id": 65},
    "Video Stream Chroma Sub Sampling": {
        "field": "Media/Part/Stream[@streamType=1]/@chromaSubsampling",
        "ReqLevel": 2,
        "id": 66},
    "Video Stream Cabac": {
        "field": "Media/Part/Stream[@streamType=1]/@cabac",
        "ReqLevel": 2,
        "id": 67},
    "Video Stream Anamorphic": {
        "field": "Media/Part/Stream[@streamType=1]/@anamorphic",
        "ReqLevel": 2,
        "id": 68},
    "Video Stream Language Code": {
        "field": "Media/Part/Stream[@streamType=1]/@languageCode",
        "ReqLevel": 2,
        "id": 69},
    "Video Stream Language": {
        "field": "Media/Part/Stream[@streamType=1]/@language",
        "ReqLevel": 2,
        "id": 70},
    "Video Stream Bitrate": {
        "field": "Media/Part/Stream[@streamType=1]/@bitrate",
        "ReqLevel": 2,
        "id": 71},
    "Video Stream Bit Depth": {
        "field": "Media/Part/Stream[@streamType=1]/@bitDepth'",
        "ReqLevel": 2,
        "id": 72},
    "Video Stream Duration": {
        "field": "Media/Part/Stream[@streamType=1]/@duration",
        "ReqLevel": 2,
        "id": 73},
    "Video Stream Level": {
        "field": "Media/Part/Stream[@streamType=1]/@level",
        "ReqLevel": 2,
        "id": 74},
    "Audio Stream Selected": {
        "field": "Media/Part/Stream[@streamType=2]/@selected",
        "ReqLevel": 2,
        "id": 75},
    "Audio Stream Default": {
        "field": "Media/Part/Stream[@streamType=2]/@default",
        "ReqLevel": 2,
        "id": 76},
    "Audio Stream Codec": {
        "field": "Media/Part/Stream[@streamType=2]/@codec",
        "ReqLevel": 2,
        "id": 77},
    "Audio Stream Index": {
        "field": "Media/Part/Stream[@streamType=2]/@index",
        "ReqLevel": 2,
        "id": 78},
    "Audio Stream Channels": {
        "field": "Media/Part/Stream[@streamType=2]/@channels",
        "ReqLevel": 2,
        "id": 79},
    "Audio Stream Bitrate": {
        "field": "Media/Part/Stream[@streamType=2]/@bitrate",
        "ReqLevel": 2,
        "id": 80},
    "Audio Stream Language": {
        "field": "Media/Part/Stream[@streamType=2]/@language",
        "ReqLevel": 2,
        "id": 81},
    "Audio Stream Language Code": {
        "field": "Media/Part/Stream[@streamType=2]/@languageCode",
        "ReqLevel": 2,
        "id": 82},
    "Audio Stream Audio Channel Layout": {
        "field": "Media/Part/Stream[@streamType=2]/@audioChannelLayout",
        "ReqLevel": 2,
        "id": 83},
    "Audio Stream Bit Depth": {
        "field": "Media/Part/Stream[@streamType=2]/@bitDepth",
        "ReqLevel": 2,
        "id": 84},
    "Audio Stream Bitrate Mode": {
        "field": "Media/Part/Stream[@streamType=2]/@bitrateMode",
        "ReqLevel": 2,
        "id": 85},
    "Audio Stream Codec ID": {
        "field": "Media/Part/Stream[@streamType=2]/@codecID",
        "ReqLevel": 2,
        "id": 86},
    "Audio Stream Duration": {
        "field": "Media/Part/Stream[@streamType=2]/@duration",
        "ReqLevel": 2,
        "id": 87},
    "Audio Stream Profile": {
        "field": "Media/Part/Stream[@streamType=2]/@profile",
        "ReqLevel": 2,
        "id": 88},
    "Audio Stream Sampling Rate": {
        "field": "Media/Part/Stream[@streamType=2]/@samplingRate",
        "ReqLevel": 2,
        "id": 89},
    "Subtitle Stream Codec": {
        "field": "Media/Part/Stream[@streamType=3]/@codec",
        "ReqLevel": 2,
        "id": 90},
    "Subtitle Stream Index": {
        "field": "Media/Part/Stream[@streamType=3]/@index",
        "ReqLevel": 2,
        "id": 91},
    "Subtitle Stream Language": {
        "field": "Media/Part/Stream[@streamType=3]/@language",
        "ReqLevel": 2,
        "id": 92},
    "Subtitle Stream Language Code": {
        "field": "Media/Part/Stream[@streamType=3]/@languageCode",
        "ReqLevel": 2,
        "id": 93},
    "Subtitle Stream Codec ID": {
        "field": "Media/Part/Stream[@streamType=3]/@codecID",
        "ReqLevel": 2,
        "id": 94},
    "Subtitle Stream Format": {
        "field": "Media/Part/Stream[@streamType=3]/@format",
        "ReqLevel": 2,
        "id": 95},
    "Subtitle Stream Title": {
        "field": "Media/Part/Stream[@streamType=3]/@title",
        "ReqLevel": 2,
        "id": 96},
    "Subtitle Stream Selected": {
        "field": "Media/Part/Stream[@streamType=3]/@selected",
        "ReqLevel": 2,
        "id": 97}
}

fieldsbyID = {
    1: "Media ID",
    2: "Title",
    3: "Sort title",
    4: "Studio",
    5: "Content Rating",
    6: "Year",
    7: "Rating",
    8: "Summary",
    9: "Genres",
    10: "View Count",
    11: "Last Viewed at",
    12: "Tagline",
    13: "Release Date",
    14: "Writers",
    15: "Country",
    16: "Duration",
    17: "Directors",
    18: "Roles",
    19: "IMDB Id",
    20: "Labels",
    21: "Locked Fields",
    22: "Extras",
    23: "Collections",
    24: "Original Title",
    25: "Added",
    26: "Updated",
    27: "Audio Languages",
    28: "Audio Title",
    29: "Subtitle Languages",
    30: "Subtitle Title",
    31: "Subtitle Codec",
    32: "Accessible",
    33: "Exists",
    34: "Video Resolution",
    35: "Bitrate",
    36: "Width",
    37: "Height",
    38: "Aspect Ratio",
    39: "Audio Channels",
    40: "Audio Codec",
    41: "Video Codec",
    42: "Container",
    43: "Video FrameRate",
    44: "Part File",
    45: "Part Size",
    46: "Part Indexed",
    47: "Part Duration",
    48: "Part Container",
    49: "Part Optimized for Streaming",
    50: "Video Stream Title",
    51: "Video Stream Default",
    52: "Video Stream Index",
    53: "Video Stream Pixel Format",
    54: "Video Stream Profile",
    55: "Video Stream Ref Frames",
    56: "Video Stream Scan Type",
    57: "Video Stream Stream Identifier",
    58: "Video Stream Width",
    59: "Video Stream Pixel Aspect Ratio",
    60: "Video Stream Height",
    61: "Video Stream Has Scaling Matrix",
    62: "Video Stream Frame Rate Mode",
    63: "Video Stream Frame Rate",
    64: "Video Stream Codec",
    65: "Video Stream Codec ID",
    66: "Video Stream Chroma Sub Sampling",
    67: "Video Stream Cabac",
    68: "Video Stream Anamorphic",
    69: "Video Stream Language Code",
    70: "Video Stream Language",
    71: "Video Stream Bitrate",
    72: "Video Stream Bit Depth",
    73: "Video Stream Duration",
    74: "Video Stream Level",
    75: "Audio Stream Selected",
    76: "Audio Stream Default",
    77: "Audio Stream Codec",
    78: "Audio Stream Index",
    79: "Audio Stream Channels",
    80: "Audio Stream Bitrate",
    81: "Audio Stream Language",
    82: "Audio Stream Language Code",
    83: "Audio Stream Audio Channel Layout",
    84: "Audio Stream Bit Depth",
    85: "Audio Stream Bitrate Mode",
    86: "Audio Stream Codec ID",
    87: "Audio Stream Duration",
    88: "Audio Stream Profile",
    89: "Audio Stream Sampling Rate",
    90: "Subtitle Stream Codec",
    91: "Subtitle Stream Index",
    92: "Subtitle Stream Language",
    93: "Subtitle Stream Language Code",
    94: "Subtitle Stream Codec ID",
    95: "Subtitle Stream Format",
    96: "Subtitle Stream Title",
    97: "Subtitle Stream Selected"
}

levels = {
    "Level_1": [1, 2, 3, 4, 5, 6, 7, 8, 9],
    "Level_2": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
    "Level_3": [20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33],
    "Level_4": [34, 35, 36, 37, 38, 39, 40, 41, 42, 43],
    "Level_5": [44, 45, 46, 47, 48, 49],
    "Level_6": [50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
                64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77,
                78, 79, 80, 81, 82, 83, 84, 85, 86, 87,
                88, 89, 90, 91, 92, 93, 94, 95, 96, 97]
}
