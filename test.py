""" Reliability Workbench RPA by Bilal El Achab\n\n- This code automates the process of changing all Logic Modes (LM) which IDs contain \'DF\' in the Fault Tree Page\n\nFirstly sets all LM to False. Then assign only 1 LM to True and saves the file.\nOnce ALL files have been saved, it performs Batch Analysis.\n\nALTEN LTD\n"""
import os
import sys
import time
from pywinauto.application import Application
from wakepy import set_keepawake, unset_keepawake
set_keepawake(keep_screen_awake=True)

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open('LOG_Batch.log', 'a')

    def write(self, message):
        self.terminal.write(message + '\n')
        self.log.write(message + '\n')

    def reset(self):
        self.log = open('LOG_Batch.log', 'w')

    def flush(self):
        return
sys.stdout = Logger()

def get_info():
    while True:
        try:
            cellID = ReliabilityWorkbench.DataGridView
            cellID.wait('exists enabled visible ready')
        except:
            time.sleep(10)
            top_window = app.window(title_re='Reliability Workbench', visible_only=False)
            top_window.restore().set_focus().maximize()
            break
    Logger().write('Getting the ID names... Please Wait.')
    cells_id = [child for child in cellID.descendants() if child.element_info.control_type == 'DataItem' and 'DF' in child.legacy_properties()['Value'] and ('ID' in child.legacy_properties()['Name'])]
    id_stored = [cell.legacy_properties()['Value'] for cell in cells_id]
    Logger().write('Getting the Logic Modes... Please Wait.')
    cells_lV = [ll for ll in cellID.descendants() if ll.element_info.control_type == 'Logic mode' else None]
    all_elements_in_grid = [i.legacy_properties()['Value'] for i in cells_lV]
    id_index = all_elements_in_grid.index('ID')
    logic_mode_index = all_elements_in_grid.index('Logic mode')
    jumps_until_logicMode_value = logic_mode_index - id_index
    getting_indexes = []
    for counter in range(len(id_stored)):
        search_for_pos_of_ID = all_elements_in_grid.index(id_stored[counter])
        currentID_logicMode_value = search_for_pos_of_ID + jumps_until_logicMode_value
        if all_elements_in_grid[currentID_logicMode_value] == 'False':
            getting_indexes.append(0)
        else:  # inserted
            getting_indexes.append(1)
    Logger().write('-------- Information Retrieved Successfully --------')
    row_to_change = [i for i, x in enumerate(getting_indexes) if x == 1]
    Logger().write('     Row to be Changed: ' + str(row_to_change))
    return (row_to_change, id_stored)

def set_only_other_values_to_false(ReliabilityWorkbench, row_to_change):
    """Set ALL LM Rows to False"""  # inserted
    access_data_gridview = ReliabilityWorkbench.child_window(title='DataGridView', auto_id='dataGrid', control_type='Table')
    for k in range(len(row_to_change)):
        access_logicMode = access_data_gridview.child_window(title='Logic mode Row ' + str(row_to_change[k]), control_type='DataItem', visible_only=False)
        access_logicMode.invoke()
        time.sleep(0.5)
        ReliabilityWorkbench.type_keys('F{ENTER}')

def continue_from_last_time(rw_dfs_folder, id_stored):
    files_to_export_check = [file for file in os.listdir(rw_dfs_folder)]
    existing_DFs_in_new_folder = map(lambda x: x.replace('.rwb', ''), files_to_export_check)
    files_to_analyse = set(id_stored) - set(existing_DFs_in_new_folder)
    indexes_for_remaining_logicModes = []
    if len(id_stored) == len(files_to_analyse):
        index = 0
    else:  # inserted
        for counter in range(len(id_stored)):
            if id_stored[counter] in files_to_analyse:
                indexes_for_remaining_logicModes.append(1)
            else:  # inserted
                indexes_for_remaining_logicModes.append(0)
                pass
        id_stored[0].replace(':', '')
        try:
            new_index = indexes_for_remaining_logicModes.index(1, 1)
        except ValueError:
            index = len(id_stored)
        index = new_index
    Logger().write('Files to be Saved with the New Logic Mode: ' + str(len(files_to_analyse)))
    return index

def set_logicmode(ReliabilityWorkbench, j):
    """Sets the corresponding LM Row to True and sets the previous one to False"""  # inserted
    access_data_gridview = ReliabilityWorkbench.child_window(title='DataGridView', auto_id='dataGrid', control_type='Table')
    access_data_gridview.wait('exists enabled ready visible', timeout=300)
    Logger().write('Accessing row...')
    while True:
        try:
            row = access_data_gridview.child_window(title='Logic mode Row ' + str(j), control_type='DataItem', visible_only=False).wait('exists')
            row.invoke()
            time.sleep(0.5)
            ReliabilityWorkbench.type_keys('T{ENTER}')
        except:
            Logger().write('A problem occurred. Maybe File Already exists and could not continue because of the pop-up at the Save As window.')
            try:
                ReliabilityWorkbench.SaveAs.Yes.click()
            finally:  # inserted
                pass  # postinserted
            break
    if j > 0:
        prev_row = access_data_gridview.child_window(title='Logic mode Row ' + str(j - 1), control_type='DataItem', visible_only=False).wait('exists')
        prev_row.invoke()
        ReliabilityWorkbench.type_keys('F{ENTER}')
        ReliabilityWorkbench.type_keys('T{ENTER}')

def save_as(ReliabilityWorkbench, id_stored):
    Logger().write('******** Opening Save As Window......********')
    while True:
        try:
            ReliabilityWorkbench = app.window(title_re='.*Reliability Workbench')
            accessing_top_bar = ReliabilityWorkbench.child_window(title='Main menu', auto_id='standardMenu')
            accessing_top_bar.wait('exists enabled visible ready')
            access_file = accessing_top_bar.child_window(title='Add', control_type='MenuItem')
            access_file.click_input()
            access_file = accessing_top_bar.child_window(title='File', control_type='MenuItem')
            access_file.wait('exists enabled visible ready')
            access_file.click_input()
        except Exception as e:
            Logger().write('File Dropdown Accessing Error.')
            Logger().write(f'The error: ({str(e)}')
            time.sleep(1)
        try:
            saveas_selection = access_file.child_window(title='Save Project As...', control_type='MenuItem', visible_only=False)
            saveas_selection.click_input()
        except:
            Logger().write('Problem occurred accessing Save As window. Trying again...')
            Logger().write(f'The error: ({str(e)}')
            time.sleep(3)
            try:
                Logger().write('Save As window accessed successfully.')
                window_save_as = ReliabilityWorkbench.child_window(title='Save As', control_type='Window')
                write_save_as = window_save_as.child_window(title='File name:', control_type='Edit')
                write_save_as.wait('exists enabled visible ready')
                if write_save_as.exists():
                    break
            except:
                pass
    Logger().write('     Save As Window opened.')
    window_save_as = ReliabilityWorkbench.child_window(title='Save As', control_type='Window')
    write_save_as = window_save_as.child_window(title='File name:', control_type='Edit')
    write_save_as.wait('exists enabled visible ready')
    write_save_as.type_keys(rw_dfs_folder + '\\' + str(id_stored[j]).replace(':', ''), with_spaces=True)
    Logger().write('     ID name written. ' + str(id_stored[j]))
    window_save_as.type_keys('{ENTER}')

def run_batch_analysis(ReliabilityWorkbench, rw_dfs_folder):
    while True:
        try:
            accessing_top_bar = ReliabilityWorkbench.child_window(title='Main menu', auto_id='standardMenu')
            accessing_top_bar.wait('exists enabled visible ready')
            access_analysis = accessing_top_bar.child_window(title='Analysis', control_type='MenuItem')
            access_analysis.wait('exists enabled visible ready')
            access_analysis.click_input()
        except:
            pass
            try:
                batch_selection = access_analysis.child_window(title='Perform Batch Analysis...', control_type='MenuItem', visible_only=False)
                batch_selection.click_input()
            except:
                pass
                window_analysis = ReliabilityWorkbench.child_window(title='Batch Analysis', control_type='Window')
                window_batch_analysis = window_analysis.child_window(title='Add Projects...', control_type='Button')
                window_batch_analysis.wait('exists enabled visible ready')
                if window_batch_analysis.exists():
                    break
    window_batch_analysis.click_input()
    files_to_export = [file for file in os.listdir(rw_dfs_folder)]
    Logger().write('******** Opening projects......********')
    window_project_name = window_analysis.child_window(title='Open', control_type='Window')
    write_projectName = window_project_name.child_window(title='File name:', control_type='Edit')
    window_project_name.wait('exists enabled visible ready')
    Logger().write('     Window opened.')
    write_projectName.set_text(rw_dfs_folder)
    window_project_name.OpenButton3.click_input()
    write_projectName.set_text(str(files_to_export).replace('[', '').replace(']', '').replace(',', '').replace('.rwb', '').replace('\'', '\"'))
    Logger().write('     File name written.')
    window_project_name.OpenButton3.click_input()
    time.sleep(10)
    window_analysis.Button13.click_input()
output_folder = input('Remember to have Reliability open with the file to be analysed, and Applied the Filter. Please enter the PATH where you want the OUTPUT FOLDER to be located. ')
app = Application(backend='uia')
app.connect(path='ReliabilityWorkbench.exe', timeout=250)
app.top_window().wait('exists enabled visible ready', timeout=100)
Logger().reset()
ReliabilityWorkbench = app.top_window()
if ReliabilityWorkbench:
    Logger().write('Successfully connected to ReliabilityWorkbench.')
ReliabilityWorkbench = app.window(title_re='.*Reliability Workbench')
rw_dfs_folder = output_folder
if rw_dfs_folder[(-1)]!= '\\':
    rw_dfs_folder += '\\'
rw_dfs_folder = rw_dfs_folder + 'RW_DFs_Folder'
os.makedirs(rw_dfs_folder) if not os.path.exists(rw_dfs_folder) else Exception(Logger().write('DFS Folder already exists!'))
Logger().write('Selected Path: ' + rw_dfs_folder)
Logger().write('******** Getting all the available information......********')
row_to_change, id_stored = get_info()
Logger().write('-------- Information Obtained Successfully --------')
Logger().write('******** Changing all the DF Rows to False......********')
set_only_other_values_to_false(ReliabilityWorkbench, row_to_change)
Logger().write('-------- All DFs changed to False Successfully --------')
Logger().write('******** Checking the files to be exported to CSV......********')
index = continue_from_last_time(rw_dfs_folder, id_stored)
placeholder_index = index
Logger().write('******** Starting Loop......********')
for j in range(index, len(id_stored)):
    Logger().write('      Selecting LM : ' + str(j + 1))
    set_logicmode(ReliabilityWorkbench, j)
    Logger().write('      LM: ' + str(j + 1) + ' Accessed Successfully')
    Logger().write('      Save As : ' + str(j + 1))
    save_as(ReliabilityWorkbench, id_stored)
    pop_up_message_saveAs = ReliabilityWorkbench.child_window(title='Confirm Save As', control_type='Window')
    if j == placeholder_index and j!= 0 and pop_up_message_saveAs.exists():
        try:
            pop_up_message_saveAs.wait('exists enabled visible ready')
            pop_up_message_saveAs.Yes.click()
        except:
            ReliabilityWorkbench.ConfirmSaveAs.Yes.click()
            if False:
                pass  # postinserted
    Logger().write('      Save As: ' + str(j + 1) + ' Saved Successfully')
    Logger().write('=============== File saved: ' + str(id_stored[j]) + ' ===============')
    Logger().write('===========================================================================')
Logger().write('-------- Loop Finished. --------')
Logger().write('Running Batch Analysis')
run_batch_analysis(ReliabilityWorkbench, rw_dfs_folder)
unset_keepawake()
