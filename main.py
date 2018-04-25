import os, glob
from func import calibrations, excitations, execution, models
from func.LoadModel import LoadModel
from func.Generate_trial_xml import generate_trial_xml
from func.CeinmWriter import CeinmWriter, SetupCalib, SetupTrial

if os.environ['COMPUTERNAME'] =='DESKTOP-4KTED5M':
    base_path = "C:/Users/micka/Dropbox/Projet_EMGdriven/test_1/"
    ceinms_path = "C:/Programming/CEINMS_dev/bin"
else:
    ceinms_path = "~/Documents/Laboratoire/Programmation/CEINMS/ceinms/release/bin"
    base_path = "TODO"


# # # DEFINE DoF, MODELS and SUBJECT, vCalibTrials, Trials # # #
DoF = 'G' # 'G' | 'SAG"
ModelName = 'Wu' # "Wu"| 'DAS3'
Subject = 'DapO'
vCalibTrials = 1
Trials = 'All' # | 'All' | 'AllButCalib' | 'Calib'
vTendon = 'stiff' #| 'elastic'
# # # END OF THE MAIN VARIABLES # # #

SubjectPath = "./%s/Trials/" % (Subject)
Model = LoadModel(ModelName)

if Model["ModelName"].lower() == 'wu' or Model["ModelName"].lower() == 'das3':
    if DoF.lower() == 'g': DoFName = Model["DoFName"][-3:]
elif DoF.lower() =='sag':  DoFName = Model["DoFName"][0:2] + Model["DoFName"][3:] #improve?

print("DoF for CEINMS are: "); print(DoFName)

# # # GENERATE trials.xml # # #
for subdir in next(os.walk(os.path.join(base_path, SubjectPath)))[1]: #regarder tous les dossiers et générer les xml
    fname = os.path.join(base_path, SubjectPath, subdir+'.xml')
    if subdir.startswith(Model["ModelName"].lower()) and not os.path.isfile(fname):
        print("Generate xml for trial: " + subdir)
        generate_trial_xml(Model, os.path.join(base_path, SubjectPath, subdir), fname)



# # # CHOOSE CalibTrials and Trials # # #
# xHy_z   with x=6|12|18 y=1-6  z=1-3
if vCalibTrials == 1:
    calib_trials = [] #initialiser avec un mouvement fonctionnel
    x=[6, 12, 18] #kg
    y=1 #changer pour excentric yeux -> hanches qd tout généré par Romain
    z=1 #x= all,
    for i in x:
        calib_trials = calib_trials + glob.glob("%s/%s*%d*%d_%d.xml" %(os.path.join(base_path, SubjectPath), ModelName.lower(), i, y, z))
else:
    print("%d: HAS TO BE DONE" %(vCalibTrials))


if Trials.lower() == 'all':
    trials = glob.glob("%s/%s*.xml" % (os.path.join(base_path, SubjectPath), ModelName.lower()))
elif Trials.lower() == 'allbutcalib':
    trials = glob.glob("%s/%s*.xml" % (os.path.join(base_path, SubjectPath), ModelName.lower()))
    for i in calib_trials:
        trials.remove(i)
elif Trials.lower() == 'calib':
    trials = calib_trials

calib_trials = tuple(calib_trials) #calib_trials = ("../../../DapO/Trials/F6H1_1.xml", "../../../DapO/Trials/F6H1_1.xml")
print('********* Calibration Files **********'); print(calib_trials)
trials = tuple(trials)
print('********* Files of Interest **********'); print(trials) #trials = ("../../Trials/F6H1_1.xml", "../../Trials/F6H1_1.xml")


# # # CALIB # # #
setup_calib = SetupCalib()
setup_calib.uncalibrated_model = models.Wu()   #  GenerateSubject(DoFName)  # TODO by Benjamin
setup_calib.excitation = excitations.Wu_v3()
setup_calib.calibration = calibrations.Wu_GH_v1(calib_trials, DoFName, vTendon, Model)
setup_calib.force_calibration = False
#################

# # # TRIALS # # #
setup_trials = SetupTrial()
setup_trials.execution = execution.EMG_driven(DoFName, vTendon) # EMG_driven Hybrid
setup_trials.allow_override = True
##################

# Write configuration and calibration files
cw = CeinmWriter(base_path, setup_calib, ceinms_path)

# Run calibration process if needed
cw.calibrate()

# Run
if isinstance(trials, tuple):
    for trial in trials:
        setup_trials.trial = trial
        cw.run(setup_trials)
else:
    setup_trials.trial = trials
    cw.run(setup_trials)
