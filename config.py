import time
config = {"fallback":{"repo": r'',
					  "workingRepoDir": r'', # Directory where SVN local repo exists
					  "tempDir": r'', # Directory where files will be temporarily stored. (lots of writing/reading)
					  "hlExtractDir": r'R:\Diffs\tools\hlextract', # Directory where HLExtract.exe resides
					  "gameFolder": r'', # The in which the game resides
					  "vpks": [], # Any VPKs that need to be unpacked for the diff, relative to gameFolder
					  "diffOutput": r'', # Location and name of file for raw svn diff output
					  "repoUser": r'', # SVN repo username
					  "repoPassword": r'', # SVN repo password
					  "patchNameFormat": r"%B %d, %Y Patch",
					  "wikiApi": r"http://www.dota2wiki.com/api.php",
					  "wikiUsername": r"RBotson",
					  "wikiPassword": r""
					  },
		 "dota2beta": {"repo": r'file:///R:/Diffs/repositories/dota2beta',
					   "workingRepoDir": r'R:\Diffs\working_repos\dota2beta',
					   "tempDir": r'R:\Diffs\raw_files\dota2beta',
					   "gameFolder": r'R:\Diffs\raw_steam\steamapps\common\dota 2 beta',
					   "vpks": [r"dota\pak01_dir.vpk", r"platform\pak01_dir.vpk"],
					   "diffOutput": r'R:\Diffs\raw_diffs\dota2beta_{generate_time!s}.txt'.format(generate_time = time.mktime(time.gmtime())),
					   "patchNameFormat": r"%B %d, %Y Patch"
					   },
		 "dota2test": {"repo": r'file:///R:/Diffs/repositories/dota2test',
					   "workingRepoDir": r'R:\Diffs\working_repos\dota2test',
					   "tempDir": r'R:\Diffs\raw_files\dota2test',
					   "gameFolder": r'R:\Diffs\raw_steam\steamapps\common\dota 2 test',
					   "vpks": [r"dota\pak01_dir.vpk", r"platform\pak01_dir.vpk"],
					   "diffOutput": r'R:\Diffs\raw_diffs\dota2test_{generate_time!s}.txt'.format(generate_time = time.mktime(time.gmtime())),
					   "patchNameFormat": r"%B %d, %Y Patch (Test)"
					   }
		}
