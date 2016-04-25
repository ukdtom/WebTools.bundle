######################################################################################################################
#	Language helper unit					
#
#	Author: dane22, a Plex Community member
#
# This unit works with supported languages within Plex
#
# NAME variable must be defined in the calling unit, and is the name of the application
#
######################################################################################################################

import json, sys


class language(object):
	init_already = False

	ISO639_3 = {
		"Unknown" : "unk",
		"Afar" : "aar",
		"Abkhazian" : "abk",
		"Afrikaans" : "afr",
		"Akan" : "aka",
		"Albanian" : "alb",
		"Amharic" : "amh",
		"Arabic" : "ara",
		"Aragonese" : "arg",
		"Armenian" : "arm",
		"Assamese" : "asm",
		"Avaric" : "ava",
		"Avestan" : "ave",
		"Aymara" : "aym",
		"Azerbaijani" : "aze",
		"Bashkir" : "bak",
		"Bambara" : "bam",
		"Basque" : "baq",
		"Belarusian" : "bel",
		"Bengali" : "ben",
		"Bihari" : "bih",
		"Bislama" : "bis",
		"Bosnian" : "bos",
		"Breton" : "bre",
		"Bulgarian" : "bul",
		"Burmese" : "bur",
		"Catalan" : "cat",
		"Chamorro" : "cha",
		"Chechen" : "che",
		"Chinese" : "chi",
		"ChurchSlavic" : "chu",
		"Chuvash" : "chv",
		"Cornish" : "cor",
		"Corsican" : "cos",
		"Cree" : "cre",
		"Czech" : "cze",
		"Danish" : "dan",
		"Divehi" : "div",
		"Dutch" : "dut",
		"Dzongkha" : "dzo",
		"English" : "eng",
		"Esperanto" : "epo",
		"Estonian" : "est",
		"Ewe" : "ewe",
		"Faroese" : "fao",
		"Fijian" : "fij",
		"Finnish" : "fin",
		"French" : "fre",
		"Frisian" : "fry",
		"Fulah" : "ful",
		"Georgian" : "geo",
		"German" : "ger",
		"Gaelic" : "gla",
		"Irish" : "gle",
		"Galician" : "glg",
		"Manx" : "glv",
		"Greek" : "ell",
		"Guarani" : "grn",
		"Gujarati" : "guj",
		"Haitian" : "hat",
		"Hausa" : "hau",
		"Hebrew" : "heb",
		"Herero" : "her",
		"Hindi" : "hin",
		"HiriMotu" : "hmo",
		"Croatian" : "hrv",
		"Hungarian" : "hun",
		"Igbo" : "ibo",
		"Icelandic" : "ice",
		"Ido" : "ido",
		"SichuanYi" : "iii",
		"Inuktitut" : "iku",
		"Interlingue" : "ile",
		"Interlingua" : "ina",
		"Indonesian" : "ind",
		"Inupiaq" : "ipk",
		"Italian" : "ita",
		"Javanese" : "jav",
		"Japanese" : "jpn",
		"Kalaallisut" : "kal",
		"Kannada" : "kan",
		"Kashmiri" : "kas",
		"Kanuri" : "kau",
		"Kazakh" : "kaz",
		"Khmer" : "khm",
		"Kikuyu" : "kik",
		"Kinyarwanda" : "kin",
		"Kirghiz" : "kir",
		"Komi" : "kom",
		"Kongo" : "kon",
		"Korean" : "kor",
		"Kuanyama" : "kua",
		"Kurdish" : "kur",
		"Lao" : "lao",
		"Latin" : "lat",
		"Latvian" : "lav",
		"Limburgan" : "lim",
		"Lingala" : "lin",
		"Lithuanian" : "lit",
		"Luxembourgish" : "ltz",
		"LubaKatanga" : "lub",
		"Ganda" : "lug",
		"Macedonian" : "mac",
		"Marshallese" : "mah",
		"Malayalam" : "mal",
		"Maori" : "mao",
		"Marathi" : "mar",
		"Malay" : "may",
		"Malagasy" : "mlg",
		"Maltese" : "mlt",
		"Moldavian" : "mol",
		"Mongolian" : "mon",
		"Nauru" : "nau",
		"Navajo" : "nav",
		"SouthNdebele" : "nbl",
		"NorthNdebele" : "nde",
		"Ndonga" : "ndo",
		"Nepali" : "nep",
		"NorwegianNynorsk" : "nno",
		"NorwegianBokmal" : "nob",
		"Norwegian" : "nor",
		"Chichewa" : "nya",
		"Occitan" : "oci",
		"Ojibwa" : "oji",
		"Oriya" : "ori",
		"Oromo" : "orm",
		"Ossetian" : "oss",
		"Panjabi" : "pan",
		"Persian" : "per",
		"Pali" : "pli",
		"Polish" : "pol",
		"Portuguese" : "por",
		"Pushto" : "pus",
		"Quechua" : "que",
		"RaetoRomance" : "roh",
		"Romanian" : "rum",
		"Rundi" : "run",
		"Russian" : "rus",
		"Sango" : "sag",
		"Sanskrit" : "san",
		"Serbian" : "scc",
		"Serbian" : "srp",
		"Sinhalese" : "sin",
		"Slovak" : "slo",
		"Slovenian" : "slv",
		"Sami" : "sme",
		"Samoan" : "smo",
		"Shona" : "sna",
		"Sindhi" : "snd",
		"Somali" : "som",
		"Sotho" : "sot",
		"Spanish" : "spa",
		"Sardinian" : "srd",
		"Swati" : "ssw",
		"Sundanese" : "sun",
		"Swahili" : "swa",
		"Swedish" : "swe",
		"Tahitian" : "tah",
		"Tamil" : "tam",
		"Tatar" : "tat",
		"Telugu" : "tel",
		"Tajik" : "tgk",
		"Tagalog" : "tgl",
		"Thai" : "tha",
		"Tibetan" : "tib",
		"Tigrinya" : "tir",
		"Tonga" : "ton",
		"Tswana" : "tsn",
		"Tsonga" : "tso",
		"Turkmen" : "tuk",
		"Turkish" : "tur",
		"Twi" : "twi",
		"Uighur" : "uig",
		"Ukrainian" : "ukr",
		"Urdu" : "urd",
		"Uzbek" : "uzb",
		"Venda" : "ven",
		"Vietnamese" : "vie",
		"Volapuk" : "vol",
		"Welsh" : "wel",
		"Walloon" : "wln",
		"Wolof" : "wol",
		"Xhosa" : "xho",
		"Yiddish" : "yid",
		"Yoruba" : "yor",
		"Zhuang" : "zha",
		"Zulu" : "zul",
		"Brazilian" : "pob",
		"NoLanguage" : "unk"
	}


	# Defaults used by the rest of the class
	def __init__(self):
		# Only init once during the lifetime of this
		if not language.init_already:
			language.init_already = True
			Log.Debug('Starting language Module')
		return

	''' Grap the tornado req, and process it for a GET request'''
	def reqprocess(self, req):		
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish('Missing function parameter')
		elif function == 'getCountryCodes':
			return self.getCountryCodes(req)
		elif function == 'getMatch':
			return self.getMatch(req)
		elif function == 'getLangCodeList':
			return self.getLangCodeList(req)
		elif function == 'getCodeLangList':
			return self.getCodeLangList(req)
		elif function == 'get3CodeLangList':
			return self.get3CodeLangList(req)
		elif function == 'getLangCode3List':
			return self.getLangCode3List(req)
		else:
			req.clear()
			req.set_status(412)
			req.finish('Unknown function call')

	''' Returns an array of valid country codes '''
	def getCountryCodes(self, req):
		req.clear()
		req.set_status(200)
		req.finish(json.dumps(Locale.Language.All()))

	''' Here we return a valid country code, based on the language param '''
	def getMatch(self, req):
		code = req.get_argument('language', 'missing')
		if code == 'missing':
			req.clear()
			req.set_status(412)
			req.finish('Missing language parameter')
		# Match the code
		req.clear()
		req.set_status(200)
		req.finish(json.dumps(Locale.Language.Match(code)))

	''' Here we return an ordered jason of language:countrycode for all the valid ones '''
	def getLangCodeList(self, req):
		# Walk the darn module
		all_languages = {}
		cls = dir(Locale.Language)
		for name in cls:
			if name[0] != '_':
				if name not in ['All', 'Match', 'lock']:
					code = Locale.Language.Match(name)
					if code != 'xx':
						all_languages[name] = code
		req.clear()
		req.set_status(200)
		req.finish(json.dumps(all_languages, sort_keys=True))

	''' Here we return an ordered jason of countrycode:language for all the valid ones '''
	def getCodeLangList(self, req):
		# Walk the darn module
		all_languages = {}
		cls = dir(Locale.Language)
		for name in cls:
			if name[0] != '_':
				if name not in ['All', 'Match', 'lock']:
					code = Locale.Language.Match(name)
					if code != 'xx':
						all_languages[code] = name
		req.clear()
		req.set_status(200)
		req.finish(json.dumps(all_languages, sort_keys=True))

	''' Here we return an ordered jason of countrycode:language for all the valid ones in ISO639-3'''
	def get3CodeLangList(self, req):
		all_languages = {}
		for key, value in self.ISO639_3.iteritems():
			all_languages[value] = key				
		req.clear()
		req.set_status(200)
		req.finish(json.dumps(all_languages, sort_keys=True))

	''' Here we return an ordered jason of language:countrycode for all the valid ones in ISO639-3'''
	def getLangCode3List(self, req):
		req.clear()
		req.set_status(200)
		req.finish(json.dumps(self.ISO639_3, sort_keys=True))








