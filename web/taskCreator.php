<?php
  echo '<?xml version="1.0" encoding="UTF-8"?>';
  include('config.php');

  function generateOptionList($aList)
  {
    for ($i = 0; $i < count($aList); $i++) {
      echo '<option>'.$aList[$i].'</option>';
    }
  }
?>

<!-- -*- Mode: HTML; tab-width: 2; indent-tabs-mode:nil; -*- -->
<!-- vim: set ts=2 et sw=2 tw=80: !-->
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>Task Creator</title>
    <!-- Copyright (c) 2011 Design Science, Inc.
         License: Apache License 2.0 -->
    <link rel="stylesheet" type="text/css" href="default.css"/>
    <script type="text/javascript" src="taskCreator.js"></script>
  </head>

  <body onload="init()">
    <div class="related">
      <h3>Navigation</h3>
      <ul>
        <li><a href="./">Back to home</a></li> 
        <li><a href="./taskViewer.php">Task Viewer</a></li> 
      </ul>
    </div>  

    <div class="body">
      <h1>Task Creator</h1>
      
      <form action="taskEditor.php" method="post">

        <fieldset>
          <legend>Task</legend>
          <p>
            <label>task name:
              <input name="taskName" type="text" required="required"
                     pattern="([a-z]|[A-Z]|[0-9]){1,20}"
                     value="<?php echo $DEFAULT_TASK_NAME;?>"
                     maxlength="20"/></label> (alphanumeric)
          </p>
          <p>
            <label>outputDirectory:
            <input name="outputDirectory" type="text"
                   pattern="([a-z]|[A-Z]|[0-9])*" maxlength="20"
                   value=""/>
            </label> (optional, default is task name)
          </p>
          <p>
            <label>schedule task:
              <input id="scheduled" name="taskSchedule" type="checkbox"
                     onchange="updateScheduleFieldVisibility()"/>
            </label>
            <span id="crontabParameters" style="visibility: hidden;">
            <span>day: 
            <select name="crontabDow">
              <option>*</option>
              <option>Monday</option>
              <option>Tuesday</option>
              <option>Wednesday</option>
              <option>Thursday</option>
              <option>Friday</option>
              <option>Saturday</option>
              <option>Sunday</option>
            </select>
            <select name="crontabDom">
              <option>*</option>
              <?php
                for ($i = 1; $i <= 31; $i++) {
                  echo '<option>'.$i.'</option>';
                }
              ?>
            </select>
            <select name="crontabMon">
              <option>*</option>
              <option>January</option>
              <option>February</option>
              <option>March</option>
              <option>April</option>
              <option>May</option>
              <option>June</option>
              <option>July</option>
              <option>August</option>
              <option>September</option>
              <option>October</option>
              <option>November</option>
              <option>December</option>
            </select>
            </span>
            <span>time:
              <select name="crontabH">
                <option>*</option>
                <?php
                  for ($i = 0; $i < 24; $i++) {
                    echo '<option>'.$i.'</option>';
                  }
                ?>
              </select> :
              <select name="crontabM">
                <option>*</option>
                <?php
                  for ($i = 0; $i < 60; $i++) {
                    echo '<option>'.$i.'</option>';
                  }
                ?>
              </select>
            </span>

            (<a href="http://en.wikipedia.org/wiki/Cron">cron syntax</a>)
            </span>
          </p>
        </fieldset>

        <fieldset>
          <legend>Framework:</legend>
          <p>
            <label>host:
              <input id="host" name="host" type="text" required="required"
                     pattern="([a-z]|[A-Z]|[0-9]|-|\.)+"
                     value=""
                     maxlength="255"/>
            </label> (or choose among known hosts:
            <select id="host_select" onchange="updateHostField()">
              <?php generateOptionList($KNOWN_HOSTS); ?>
            </select>)

          </p>
          <p>
            <label>port:
              <input name="port" type="text"
                     value="<?php echo $DEFAULT_SELENIUM_PORT;?>"/>
            </label>
          </p>
          <p>
            <label>mathJaxPath:
              <input name="mathJaxPath" type="text" size="50"
                     value="<?php echo $DEFAULT_MATHJAX_PATH;?>"/>
            </label>
          </p>
          <p>
            <label>mathJaxTestPath:
              <input name="mathJaxTestPath" type="text" size="50"
                     value="<?php echo $DEFAULT_MATHJAX_TEST_PATH;?>"/>
            </label>
          </p>
          <p>
            <label>timeOut:
              <input name="timeOut" type="number" min="1" max="120"
                     value="<?php echo $DEFAULT_TIMEOUT/1000?>"/> (seconds)
            </label>
          </p>
          <p>
            <label>fullScreenMode:
              <input name="fullScreenMode" type="checkbox" checked="checked"/>
            </label>
          </p>
          <p>
            <label>formatOutput:
              <input name="formatOutput" type="checkbox" checked="checked"/>
            </label>
          </p>
          <p>
            <label>compressOutput:
              <input name="compressOutput" type="checkbox" checked="checked"/>
            </label>
          </p>
        </fieldset>

        <fieldset>
          <legend>Platform:</legend>
          <p>
            <label>operatingSystem:
              <select name="operatingSystem">
                <?php generateOptionList($OS_LIST); ?>
              </select>
            </label>
          </p>
          <p>
            <label>browser:
              <select name="browser">
              <?php generateOptionList($BROWSER_LIST); ?>
              </select>
            </label>
          </p>
          <p>
            <label>browserMode (MSIE):
              <select name="browserMode">
              <?php generateOptionList($BROWSER_MODE_LIST); ?>
              </select>
            </label>
          </p>
          <p>
            <label>browserPath:
              <input name="browserPath" type="text" value="auto"
                     readonly="readonly"/>
            </label>
          </p>
          <p>
            <label>font:
              <select name="font">
              <?php generateOptionList($FONT_LIST); ?>
              </select>
            </label>
          </p>
          <p>
            <label>nativeMathML:
              <input name="nativeMathML" type="checkbox"/>
            </label>
          </p>
        </fieldset>

        <fieldset>
          <legend>Testsuite:</legend>
          <p>
            <label>runSlowTests:
              <input name="runSlowTests" type="checkbox" checked="checked"/>
            </label>
          </p>
          <p>
            <label>runSkipTests:
              <input name="runSkipTests" type="checkbox"/>
            </label>
          </p>
          <p>
            <label>listOfTests:
              <input id="listOfTests"
                     name="listOfTests" type="text" value="all" size="50"
                     pattern="(all|([0-2]+))"/>
            </label>
            <a href="javascript:openReftestSelector();">Reftest Selector</a>
          </p>
          <p>
            <label>startID:
              <input name="startID" type="text" value="" size="50"
                     pattern="([a-z]|[A-Z]|[0-9]|_|-|\.|/)+" />
            </label> (optional, used for test recovery) 
          </p>
        </fieldset>

        <p style="visibility: hidden; height: 0;">
            <input name="command" type="text"
                   value="ADD" readonly="readonly"/>
        </p>

        <p style="text-align: right;">
          <input type="submit" value="Create new task"/>
        </p>

      </form>

    </div>
  </body>
</html>
