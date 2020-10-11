
import time
import sys

# get passwords unix style (no characters appear in the console)
from getpass import getpass

import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import \
  NoSuchElementException, TimeoutException, NoAlertPresentException

from selenium.webdriver.common.action_chains import ActionChains


class DeleteJournalIDsFromConcilioDatabaseViaNextVIPWebpage:
  
  _driver = None

  def __init__(self):
    pass


  def get_driver(s) -> selenium.webdriver:
    '''try to return Firefox or Chrome webdriver
    
       Note: If successful getting a *Chrome* WebDriver, there will be
             an instance of 'chromedriver.exe' that remains open in the
             task manager (in Windows) even after python ends and the user
             closes the browser window.
             This happens because the 'classObj' (which contains the
             webdriver) is a global and is still in scope when python
             finishes.
             These instances remain in task manager until system restart.
             This is sub-optimal, but is the only way to keep the browser
             window open after the script has finished.
             Firefox does not suffer the same problem.'''

    if s._driver:
      return s._driver
    else:
    
      # try firefox

      try:
        s._driver = webdriver.Firefox(
          executable_path =  'webdrivers/geckodriver(win64,Jan2019).exe')
        print('returning a firefox selenium driver')
        return s._driver
      except:
        pass

      # try chrome
      # different chromedrivers work for different versions of Chrome

      # Could not get selenium to pass on chrome options to supress
      # debug output from chromedriver being printed to console

      options = webdriver.ChromeOptions()
      options.add_argument("start-maximized")
      # remove msg 'Chrome is being controlled by automated test software'
      options.add_argument('disable-infobars')
      
      # log is overwriten each time driver starts
      service_log_path = 'webdrivers/chromedriver.log'
      
      
      try:
        s._driver = webdriver.Chrome \
          (options          = options
          ,executable_path  = 'webdrivers/chromedriver(win32,Aug2019).exe'
          ,service_log_path = service_log_path
          )
        return s._driver
      except:
        pass

      try:
        s._driver = webdriver.Chrome \
          (options          = options
          ,executable_path  = 'webdrivers/chromedriver(win32,Jun2019).exe'
          ,service_log_path = service_log_path
          )
        return s._driver
      except:
        pass

      try:
        s._driver = webdriver.Chrome \
          (options          = options
          ,executable_path  = 'webdrivers/chromedriver(win64,Jan2019).exe'
          ,service_log_path = service_log_path
          )
        return s._driver
      except:
        pass
    
      return s._driver

  def login(s):
    print('checking/calling for a selenium driver now')
    if (not s.get_driver()):
      print('raising an exception')
      raise Exception
    
    print('logging into OutSystems NextVIP')
    s._driver.get('https://www.concilio.app/nextvip/TrxProcessLogs.aspx')
    
    # stderr used so rest of output can be piped to a logfile
    username = getpass("Please enter your NextVIP (Concilio) username: ", stream=sys.stderr)
    pwd = getpass("Please enter your NextVIP (Concilio) pwd: ", stream=sys.stderr)

    # added so program cannot be run accidentily
    print(""
         ,"comment out this line to run the program further"
         ,"(safeguard against accidental execution)"
         ,""
         ,sep='\n'
         )
    sys.exit()
    
    username_field = s._driver.find_element_by_id(
      'VanillaTheme_wt35_block_wtMainContent_wtUserNameInput')
    username_field.clear()
    username_field.send_keys(username)
    
    pwd_field = s._driver.find_element_by_id(
      'VanillaTheme_wt35_block_wtMainContent_wtPasswordInput')
    pwd_field.clear()
    pwd_field.send_keys(pwd + Keys.RETURN)

      
  def NextVIP(s, p_JNLID) -> None:
    assert(type(p_JNLID) == str)  

    def open_Process_Log_Page():
      '''return 0 on success
         return 1 if couldn't load Process Log Page
         return 2 if couldn't find journal after searching
         return 3 if page didn't load in time so log found was not ours'''
      
      print(p_JNLID, "opening Process Log Page")
      
      # try loading Process Log page
      try:

        s._driver.get('https://www.concilio.app/nextvip/TrxProcessLogs.aspx')

        log_field = WebDriverWait(s._driver, 60).until(
          EC.presence_of_element_located(
            (By.ID, 'VanillaTheme_wt35_block_wtMainContent_wtSearchInput')
          )
        )
        print(p_JNLID, 'process log search field loaded')
              
        log_field.clear()
        log_field.send_keys(p_JNLID + Keys.RETURN)

      except TimeoutException:
        print(p_JNLID, "could not open Process Log Webpage\n" +
                       "(or couldn't find seach field)")
        return 1
      
      
      # try searching for journal
      try:
        time.sleep(15) # don't want to accidentally look for element on prev page

        jnl_in_table = WebDriverWait(s._driver, 60).until(
          EC.presence_of_element_located(
            (By.ID, 'VanillaTheme_wt35_block_wtMainContent_wtTrxProcessLogTable_ctl03_wt3')
          )
        )      

        if(jnl_in_table.text != p_JNLID):
          return 3
        print(p_JNLID, "journal found")
        
        jnl_in_table.click()

      except TimeoutException:
        
        try:
          jnl_in_table = WebDriverWait(s._driver, 20).until(
            EC.presence_of_element_located(
              (By.CLASS_NAME, 'TableRecords_OddLine')
            )
          )
          
          if (jnl_in_table.text == "No trx process logs to show..."):
            print(p_JNLID, "couldn't find journal after searching")
            return 2
        
        except TimeoutException:
          print(p_JNLID, "page didn't load in time")
          return 3

      return 0
      

    def del_Process_Logs():
      '''return True if sucess, False if failure'''
      
      print(p_JNLID, "deleting Process Log")
      
      # try deleting journal's process log
      try:
        time.sleep(15)
        
        select_all_checkbox = WebDriverWait(s._driver, 60).until(
          EC.presence_of_element_located(
            (By.ID, 'VanillaTheme_wt8_block_wtMainContent_wtTrxProcessLog_TrxCarryOverTransferTable_ctl02_RichWidgets_wt50_block_wtchkSelectAll')
          )
        )
        
        select_all_checkbox.click()      
      
        deletetext = WebDriverWait(s._driver, 60).until(
          EC.presence_of_element_located(
            (By.ID, 'VanillaTheme_wt8_block_wtMainContent_wtlnkDeleteSelectedTrxCarryOverTransfer')
          )
        )

        deletetext.click()
      
        time.sleep(5)      
             
        alertwin = s._driver.switch_to.alert
        alertwin.accept()

      except TimeoutException:
        print("could not delete Process Logs (could not find btn)")
        return False
      except NoAlertPresentException:
        pass

      return True

    def confirm_Process_Log_deleted_from_scratch():
      '''return 0 if deleted
         return 1 if not deleted
         return 2 if timeout'''
      
      print(p_JNLID, "confirming process log deleted (from scratch)")

      #return 0 on success
      #return 1 if couldn't load Process Log Page
      #return 2 if couldn't find log after searching
      #return 3 if page didn't load in time so log found was not ours'''
      a = open_Process_Log_Page()
       
      if a == 2:
        return 0 # Journal is deleted, thus process log is already deleted
      else:
        return 2 # internet error
      
      confirm_Process_Log_deleted_from_Process_Log_Detail_Page()


    def confirm_Process_Log_deleted_from_Process_Log_Detail_Page():
      '''return 0 if deleted
         return 1 if not deleted
         return 2 if timeout
         
         can only confirm (will only work) if JOURNAL has not already been
         deleted. else no journal will show when searching for process
         logs.
         Therefore, this function can only be run BEFORE the JOURNAL is
         deleted.
         '''

      
      print(p_JNLID, "confirming Process Log deleted (from process log Detail page)")
      
      assert 'TCR Process Log' in s._driver.title
      
      # try deleting journal's process log
      try:
        
        time.sleep(15)
       
        # 'disabled' attribute is only defined (and set to True) when
        # text IS greyed out.
        # But we need to select an item to delete before this text will
        # become enabled anyway.
        
        # click select all btn
        select_all_checkbox = WebDriverWait(s._driver, 60).until(
          EC.presence_of_element_located(
            (By.ID, 'VanillaTheme_wt8_block_wtMainContent_wtTrxProcessLog_TrxCarryOverTransferTable_ctl02_RichWidgets_wt50_block_wtchkSelectAll')
          )
        )
        
        select_all_checkbox.click()      
       
        time.sleep(2)

        deletetext = WebDriverWait(s._driver, 60).until(
          EC.presence_of_element_located(
            (By.ID, 'VanillaTheme_wt8_block_wtMainContent_wtlnkDeleteSelectedTrxCarryOverTransfer')
          )
        )
       
        # get_attribute() returns None if no attribute is defined in elem.
        # (also, returns string 'true' or 'false' rather than boolean)
        if (deletetext.get_attribute("disabled") == "true"):
          # text is greyed out
          print(p_JNLID, "confirmed deleted")
          return 0
        else:
          print(p_JNLID, "confirmed NOT deleted !!!!!!!!!!!!!!!!!!!!")
          return 1
      
      except TimeoutException:
        print(p_JNLID, "timeout, internet problem? started on wrong page?")
        return 2
      

    def openJournalHeaderDetailPage():
      '''return 0 on success
         return 1 if couldn't load Journal Header Page
         return 2 if couldn't find journal after searching
         return 3 if page didn't load in time so log found was not ours'''

      try:
        s._driver.get("https://www.concilio.app/nextvip/TCRJournalHeaders.aspx")

        tcrJrnHeader_field = WebDriverWait(s._driver, 60).until(
          EC.presence_of_element_located(
            (By.ID, 'VanillaTheme_wt40_block_wtMainContent_wtSearchInput')
          )
        )
        print(p_JNLID, 'journal search field loaded')

        tcrJrnHeader_field.clear()
        tcrJrnHeader_field.send_keys(p_JNLID + Keys.RETURN)

      except TimeoutException:
        print(p_JNLID, "could not open Process Log Webpage\n" +
                       "(or couldn't find seach field)")
        return 1

      
      try:
        time.sleep(10)

        jnl_in_table = WebDriverWait(s._driver, 20).until(
          EC.presence_of_element_located(
            (By.ID, 'VanillaTheme_wt40_block_wtMainContent_wtJournalHeaderTable_ctl03_wt13')
          )
        )

        if(jnl_in_table.text != p_JNLID):
          return 3

        print(p_JNLID, 'journal found')

        jnl_in_table.click()

        time.sleep(5)
      
      except TimeoutException:
        
        try:
          jnl_in_table = WebDriverWait(s._driver, 20).until(
            EC.presence_of_element_located(
              (By.CLASS_NAME, 'TableRecords_OddLine')
            )
          )
          
          if (jnl_in_table.text == "No journal headers to show..."):
            print(p_JNLID, "couldn't find journal after searching")
            return 2
        
        except TimeoutException:
          print(p_JNLID, "page didn't load in time")
          return 3

      return 0


    def del_Journal():
      '''return 0 if success
         return 3 if already deleted (no delete button after clickingcouldn't find 'go to TCR Journal' button)
      '''
      # we are guaranteed to be on the Journal Detail Page at start
      
      # WARNING: ONLY CALL THIS IF YOU ARE SURE PROCESS LOGS ARE DELETED
      # (it doesn't handle the situation where a constraint error
      #  prevents deletion of journal because process log has not yet
      #  been deleted)
      
      print(p_JNLID, "deleting journal")
      
      try:
        goToTcrJnlBtn = WebDriverWait(s._driver, 20).until(
          EC.presence_of_element_located(
            (By.ID, 'VanillaTheme_wt8_block_wtActions_wt14')
          )
        )
        goToTcrJnlBtn.click()

      except TimeoutException:
        print(p_JNLID, "page wasn't loaded at start of function")
        return 3

      
      try:
        jnlDeleteBtn = WebDriverWait(s._driver, 20).until(
          EC.presence_of_element_located(
            (By.ID, 'VanillaTheme_wt445_block_wtMainContent_wt236')
          )
        )
        
        jnlDeleteBtn.click()
        
        alertwin = s._driver.switch_to.alert
        alertwin.accept()

      except TimeoutException:
        print(p_JNLID, "Journal already deleted")
        # or error trying b/c log exists
      
      return 0

#      textErrorElem = WebDriverWait(s._driver, 180).until(
#        EC.presence_of_element_located(
#          (By.CLASS_NAME, 'Text_Error')
#        )
#      )
#
#      if (textErrorElem.text == "Error executing query."):
#        print("Journal Deleted sucessfully:", p_JNLID)
#      else:
#        print("Journal NOT Deleted:", p_JNLID)
#        #del_Journal()


    def del_JournalHeader():
      # we are guaranteed to be on the Journal Detail Page at start
      # WARNING: ONLY CALL THIS IF YOU ARE SURE PROCESS LOGS ARE DELETED

      print(p_JNLID, "deleting journal header")
      
      try:
        jnlDeleteBtn = WebDriverWait(s._driver, 60).until(
          EC.presence_of_element_located(
            (By.ID, 'VanillaTheme_wt8_block_wtMainContent_wt22')
          )
        )
        jnlDeleteBtn.click()
      
        alertwin = s._driver.switch_to.alert
        alertwin.accept()

        time.sleep(5)
        
      except TimeoutException:
        print(p_JNLID, "page wasn't loaded at start of function")
        return 3

      return 0


    def confirm_Journal_Deleted():
      print(p_JNLID, "confirming journal is deleted")
      
      return openJournalHeaderDetailPage() == 2


    
    #==================================================
    
    #--------------------
    # deleted process log
    #--------------------

    print(p_JNLID, "I'm going to delete the process log now")

    isDeleted = False

    # return 0 on success
    # return 1 if couldn't load Process Log Page
    # return 2 if couldn't find journal after searching
    # return 3 if page didn't load in time so log found was not ours'''
    a = open_Process_Log_Page()
    if a == 1:
      print(p_JNLID, "INTERNET ERROR")
      return
    elif a == 2:
      # journal already deleted
      print(p_JNLID, "PROCESS LOG ALREADY DELETED")
      # continue on, to check journal and journal header
      isDeleted = True
    elif a == 3:
      print(p_JNLID, "INTERNET ERROR")
      return
    
    if not isDeleted:
      if not del_Process_Logs():
        print(p_JNLID, "PROCESS LOG DELETE ERROR (at attempt)")
        return
      
      x = confirm_Process_Log_deleted_from_Process_Log_Detail_Page()
    else:
      x = confirm_Process_Log_deleted_from_scratch()
    
    # return 0 if deleted, return 1 if not deleted, return 2 if timeout
    if x == 1: # NOT deleted
      print(p_JNLID, "PROCESS LOG DELETE ERROR (at check)")
      return
    elif x == 2: # timeout
      print(p_JNLID, "INTERNET ERROR")      
      return
    
    #--------------------
    # delete journal
    #--------------------
    
    print(p_JNLID, "I'm going to delete the journal now")
    
    # return 0 on success
    # return 1 if couldn't load Process Log Page
    # return 2 if couldn't find journal after searching
    # return 3 if page didn't load in time so log found was not ours'''
    b = openJournalHeaderDetailPage()
    if b == 1:
      print(p_JNLID, "INTERNET ERROR")
      return
    elif b == 2:
      # journal already deleted
      print(p_JNLID, "JOURNAL HEADER (AND JOURNAL?) ALREADY DELETED") 
      return
    elif b == 3:
      print(p_JNLID, "INTERNET ERROR")
      return
    
    c = del_Journal()
    if b == 3:
      print(p_JNLID, "INTERNET ERROR")
      return

    print(p_JNLID, "I'm going to delete the journal header now")
        
    b = openJournalHeaderDetailPage()
    if b == 1:
      print(p_JNLID, "INTERNET ERROR")
      return
    elif b == 2:
      # journal already deleted
      print(p_JNLID, "JOURNAL HEADER (AND JOURNAL?) ALREADY DELETED") 
      return
    elif b == 3:
      print(p_JNLID, "INTERNET ERROR")
      return
    
    d = del_JournalHeader()
    if b == 3:
      print(p_JNLID, "INTERNET ERROR")
      return
    
    if not confirm_Journal_Deleted():
      print(p_JNLID, "FAILED TO CONFIRM JOURNAL HEADER DELETED ERROR")
      return

    #==================================================




#=========================================================================
# MAIN
#=========================================================================

def NextVIP() -> None:

  print(""
       ,"This selenium program was written in Sep 2019."
       ,"It's possible that the html element ids have changed since."
       ,""
       ,sep='\n'
       )

  global classObj
  classObj = DeleteJournalIDsFromConcilioDatabaseViaNextVIPWebpage()
  classObj.login()
  
  # Journal IDs to delete from Concilio Database (via NextVIP webpage)
  # these three are examples only
  for x in ["11111"
           ,"11112"
           ,"11113"
           ] :
    print()
    classObj.NextVIP(x)


if __name__ == '__main__':
  NextVIP()
