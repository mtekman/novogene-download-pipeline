from bioblend import galaxy
from os import environ as env
from os import path as path

# Get this from https://usegalaxy.eu/user/api_key
your_api_key = env["USEGALAXY_API_KEY"] ## "8fa59034518eb324dfa546a5dc67fa1f"

batch_no= env["BATCH_NO"] ## "X203_TEST_HISTORY"
has_tags= env["TAGS"] ## "datasets JD RS SP"
has_samples= env["SAMPLES"] ## "111 22"
if "REMDIR" in env:
   remote_dir=env["REMDIR"] ## an exact directory
else:
   remote_dir=False

gi = galaxy.GalaxyInstance(url="https://usegalaxy.eu", key=your_api_key)
hc = gi.histories
tc = gi.tools

ftp_files = gi.ftpfiles.get_ftp_files()

if len(ftp_files) == 0:
    print("No FTP files found...")
    exit(255)

## Attempt to match to the exact remote dir
ftp_directory = ""
if remote_dir:
   remote_dir_matches = [x['path'] for x in ftp_files if x['class'] == 'Directory' and (remote_dir in x['path'])]
   
   if len(remote_dir_matches) == 1:
       ftp_directory = remote_dir_matches[0]
   else:
       print("Could not find exact directory:", remote_dir, " defaulting to batch with the greatest date")

if ftp_directory == "":
   matching_dirs = list(
       [path.dirname(x['path']) for x in ftp_files
                                if x['class'] == 'Directory' and (("__" + batch_no) in x['path'])])
   if len(matching_dirs) == 0:
      print("No directories for batch", batch_no, " could be found")
      exit(255)
   
   ## Last directory
   ftp_directory = sorted(matching_dirs, key=lambda x: x.split("__")[0].replace("-",""))[-1]
   print("Using:", ftp_directory)

if ftp_directory == "":
   print("Could not reliably determine ftp_directory, quitting")
   exit(255)

date_uploaded = ftp_directory.split("__")[0]
files_to_move = [x['path'] for x in ftp_files if x['class'] == 'File' and (ftp_directory in x['path'])]

## Create history with name and tag
new_hist = hc.create_history(batch_no, )
hc.update_history(new_hist['id'],
                  tags=has_tags.split(),
                  annotation="Uploaded %s, contains files: %s" % (date_uploaded, has_samples))


## Move from FTP to history
for fl2m in files_to_move:
    tc.upload_from_ftp(fl2m, new_hist['id'], file_type="fastqsanger.gz")

