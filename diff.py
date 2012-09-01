import os, subprocess, re, time, sys, shutil, urllib2, chardet
from subprocess import Popen, PIPE
from prettydiff2 import poot

from config import config


def supported_games():
    output = ""
    for game in config:
        if game != "fallback":
            output += '\t {game!s}'.format(game = game)
            if game is not config.keys()[len(config) - 1]:
                output += "\n"
    return output


def compare(sourceDir, targetDir):
    """ Compare two directories and return list of missing files from the target directory """
    missing = []

    # verify existence of source directory
    if os.path.exists(sourceDir) == False:
        print "sourceDir doesn't exist: %s" % sourceDir
        sys.exit(1)

    if os.path.isdir(sourceDir) == False:
        print "sourceDir not a directory: %s" % sourceDir
        sys.exit(1)

    # verify existence of target directory
    if os.path.exists(targetDir) == False:
        print "targetDir doesn't exist: %s" % targetDir
        sys.exit(1)

    if os.path.isdir(targetDir) == False:
        print "targetDir not a directory: %s" % targetDir
        sys.exit(1)

    # walk the sourceDirectory...
    for root, dirs, files in os.walk(sourceDir):

        subDir = root.replace(sourceDir, '')
        targetSubDir = targetDir + subDir

        pattern = r'\.svn'
        regexp = re.compile(pattern, re.IGNORECASE)
        result = regexp.search(targetSubDir)
        if result:
                continue

        # check to see if targetSubDir exists
        if os.path.exists(targetSubDir) == False or os.path.isdir(targetSubDir) == False:
            print
            print "sourceDir %s not found at %s" % (root, targetSubDir)
            missing.append(root.replace('\\\\', '\\'))
            continue

        # verify that each file in root exists in targetSubDir
        count = 0
        for sourceFile in files:
            # skip symbolic links
            if os.path.islink(root + '/' + sourceFile):
                continue

            targetFile = targetSubDir + '/' + sourceFile
            if os.path.exists(targetFile) == False:

                # print header if this is the first missing file
                count = count + 1
                if count == 1:
                    print
                    print "Files in %s missing from %s" % (root, targetSubDir)
                missing.append(root.replace('\\\\', '\\') + '\\' + sourceFile)
                print "\t%s" % (sourceFile)

        # verify that each file in root is indeed a file in targetSubDir
        count = 0
        for sourceFile in files:

            # skip symbolic links
            if os.path.islink(root + '/' + sourceFile):
                continue

            targetFile = targetSubDir + '/' + sourceFile
            if os.path.exists(targetFile) == True and os.path.isfile(targetFile) == False:

                # print header if this is the first missing file
                count = count + 1
                if count == 1:
                    print
                    print "Files in %s not valid files in %s" % (root, targetSubDir)

                print "\t%s" % (sourceFile)

        # now diff the source and target files
        count = 0
        for sourceFile in files:

            # skip symbolic links
            if os.path.islink(root + '/' + sourceFile):
                continue

            targetFile = targetSubDir + '/' + sourceFile
    return missing


def moveDirectory(root_src_dir, root_dst_dir):
    for src_dir, dirs, files in os.walk(root_src_dir):
        dst_dir = src_dir.replace(root_src_dir, root_dst_dir)
        if not os.path.exists(dst_dir):
            os.mkdir(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            shutil.move(src_file, dst_dir)


def returnEncoding(string):
    encoding = chardet.detect(string)
    return encoding['encoding']


def svnDelete(filename):
    subprocess.call(r'svn delete ' + "\"" + filename + "\"")


def getPatchName(format):
    timeInUS = time.time() - (8 * 60 * 60)
    suggestion = time.strftime(format, time.localtime(timeInUS))
    if str(raw_input("Please confirm patch page name: {suggestion!s}  y\\n ".format(suggestion=suggestion))) == "y":
        semifinal = suggestion
    else:
        semifinal = str(raw_input("Manually enter the correct page name: "))

    if str(raw_input("Is this the first patch of the day? y\\n ")) == "n":
        final = semifinal + " {n}".format(n=str(raw_input("If this is the nth patch of the day, what is n?")))
    else:
        final = semifinal

    return final


def txtToUtf8(dir):
    for root, dirs, files in os.walk(dir):
        for f in files:
            if f[-4:] == r'.txt':
                try:
                    fullpath = os.path.join(root, f)
                    filecontents = open(fullpath, 'rb').read()
                    encoding = returnEncoding(filecontents)
                    utf8string = unicode(filecontents, encoding).encode("utf-8")
                    open(fullpath, 'wb').write(utf8string)
                except:
                    pass


def main():
    # Check to see which game has been specified via the launch arguments.
    if len(sys.argv) < 2:
        print 'Please specify the game to diff:'
        print supported_games()
        sys.exit(1)
    try:
        fallback = config["fallback"]
        working = config[sys.argv[1]]

        repo = working.get("repo", fallback["repo"])
        workingRepoDir = working.get("workingRepoDir", fallback["workingRepoDir"])
        tempDir = working.get("tempDir", fallback["tempDir"])
        hlExtractDir = working.get("hlExtractDir", fallback["hlExtractDir"])
        gameFolder = working.get("gameFolder", fallback["gameFolder"])
        vpks = working.get("vpks", fallback["vpks"])
        diffOutput = working.get("diffOutput", fallback["diffOutput"])
        repoUser = working.get("repoUser", fallback["repoUser"])
        repoPassword = working.get("repoPassword", fallback["repoPassword"])
        patchNameFormat = working.get("patchNameFormat", fallback["patchNameFormat"])
        wikiApi = working.get("wikiApi", fallback["wikiApi"])
        wikiUsername = working.get("wikiUsername", fallback["wikiUsername"])
        wikiPassword = working.get("wikiPassword", fallback["wikiPassword"])

        name = os.path.split(gameFolder)[1]
    except:
        print 'Error: First argument must be a supported game:'
        print supported_games()
        sys.exit(1)

    patchTitle = getPatchName(patchNameFormat)

    # Create temp directory
    if os.path.isdir(tempDir) != True:
        os.mkdir(tempDir)
    else:
        print "Johnny: \tCAPTAIN, WE HAVE REMNANTS OF AN OLD TEMPDIR!"
        print "Captain: \tARRR, THAT AINT IDEAL.  KABLEWM THE SCALLYWAGS OUTA THE OCEAN I SAY!"
        print "Johnny: \tMENTLEMENS, LASER THE BEEMZ!"
        shutil.rmtree(tempDir)
        print "Sniper: \t Thanks for standin still, ganker!"
        os.mkdir(tempDir)
    print "Copying files to temp directory"
    copyToTempdir = r'xcopy "{source!s}" "{destination!s}" /E /Q'.format(source = gameFolder, destination = tempDir)
    returnCopyToTempdir = subprocess.call(copyToTempdir, shell=True)
    if returnCopyToTempdir != 0:
        shutil.rmtree(tempDir)
        print 'Error: Shutdown the Steam client first dummkopf'
        sys.exit(1)

    missingfiles = compare(workingRepoDir + os.sep + name, tempDir)
    if len(missingfiles) != 0:
        print "\nFiles removed from files:"
        for f in missingfiles:
            svnDelete(f)
    else:
        print "\nNo files removed from files."

    # Convert .txt files to utf-8
    print "\nConverting relevant files to utf-8 and decrypting ctx files"
    txtToUtf8(tempDir)

    print "\nMoving files to working repository"
    # Moving files to repository.
    moveDirectory(tempDir, workingRepoDir + os.sep + name)

    print "\nDeleting temporary directory."
    # Delete temp directories
    shutil.rmtree(tempDir)

    # Commit changes to SVN repo
    print "\nCommitting changes to SVN repo"

    commit_message = patchTitle
    subprocess.call(['svn', 'add', workingRepoDir + os.sep + name, '--force', '--quiet'])
    subprocess.call(['svn', 'commit', workingRepoDir + os.sep, '-m', commit_message, '--username', repoUser, '--password', repoPassword, '--quiet'])

    # Get SVN diff
    print "\nDownloading SVN diff output"

    lastRevisionRE = re.compile(r'Revision: (\d+)')
    p = Popen('svn info {repo!s}'.format(repo=repo), stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    result = lastRevisionRE.search(stdout)
    currentRevision = int(result.group(1))
    lastRevision = currentRevision - 1

    q = Popen('svn diff {repo!s}@{lastRevision!s} {repo!s}@{currentRevision!s}'.format(repo=repo, lastRevision=lastRevision, currentRevision=currentRevision), stdout=PIPE, stderr=PIPE)
    stdout, stderr = q.communicate()
    open(diffOutput, "wb").write(stdout)

    #Commit to wiki
    raw_input("Ready to submit to Wiki.  Hit enter to go ahead.")
    print "\nSubmitting prettydiff to wiki"
    poot(wikiApi, wikiUsername, wikiPassword, patchTitle, diffOutput)

    print "All done!"

if __name__ == "__main__":
    main()