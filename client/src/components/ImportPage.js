//import './App.css';
import React, { useState, useEffect } from "react";

import { Link } from "react-router-dom";

function ImportPage() {
  const [file, setFile] = useState();
  const [timeStampString, setTimeStampString] = useState();
  const [timeStampColumn, setTimeStampColumn] = useState();
  const [activityColumn, setActivityColumn] = useState();
  const [traceColumn, setTraceColumn] = useState();
  const [separator, setSeparator] = useState();
  const [array, setArray] = useState([]);

  const fileReader = new FileReader();

  const handleOnChangeFile = (e) => {
    setFile(e.target.files[0]);
    handleOnSubmit(e);
  };

  const handleOnChangeTimeStampString = (e) => {
    setTimeStampString(e.target.value);
    handleOnSubmit(e);
  };

  const handleOnChangeTimeStampColumn = (e) => {
    setTimeStampColumn(e.target.value);
    handleOnSubmit(e);
  };

  const handleOnChangeActivityColumn = (e) => {
    setActivityColumn(e.target.value);
    handleOnSubmit(e);
  };

  const handleOnChangeTraceColumn = (e) => {
    setTraceColumn(e.target.value);
    handleOnSubmit(e);
  };

  const handleOnChangeSeparator = (e) => {
    setSeparator(e.target.value);
    handleOnSubmit(e);
  };

  const csvFileToArray = string => {
    const csvHeader = string.slice(0, string.indexOf("\n")).split(separator);
    const csvRows = string.slice(string.indexOf("\n") + 1).split("\n");

    const array = csvRows.map(i => {
      const values = i.split(separator);
      const obj = csvHeader.reduce((object, header, index) => {
        object[header] = values[index];
        return object;
      }, {});
      return obj;
    });

    setArray(array);
  };

  const handleOnSubmit = (e) => {
    e.preventDefault();

    if (file) {
      fileReader.onload = function (event) {
        const text = event.target.result;
        csvFileToArray(text);
      };

      fileReader.readAsText(file);
    }
  };

  const headerKeys = Object.keys(Object.assign({}, ...array));

  return (
    <div >
      <h1>IMPORT RAW EVENTLOG </h1>
      <form>
      <table>
        <tr>
        <td><label> CSV File </label></td>
        <td><input
          type={"file"}
          id={"csvFileinput"}
          accept={".csv"}
          onChange={handleOnChangeFile}
        /></td>
        </tr>
        <tr>
        <label> Separator </label>
        <td><input
          type={"text"}
          id={"separator"}
          placeholder="Separator"
          onChange={handleOnChangeSeparator}
        /></td>
        </tr>
        <tr>
        <label> Timestamp formatting String </label>
        <td><input
          type={"text"}
          id={"timeStampinput"}
          placeholder="Timestamp formatting String"
          onChange={handleOnChangeTimeStampString}
        /></td>
        </tr>
        <tr>
        <label> Timestamp Column </label>
        <td><input
          type={"number"}
          id={"timeStampColumn"}
          placeholder="Timestamp Column"
          onChange={handleOnChangeTimeStampColumn}
        /></td>
        </tr>
        <tr>
        <label> Activity Column </label>
        <td><input
          type={"number"}
          id={"activityColumn"}
          placeholder="Activity Column"
          onChange={handleOnChangeActivityColumn}
        /></td>
        </tr>
        <tr>
        <label> Trace Column </label>
        <td><input
          type={"number"}
          id={"traceColumn"}
          placeholder="Trace Column"
          onChange={handleOnChangeTraceColumn}
        /></td>
        </tr>
        <label>  </label>
        <td><button
          onClick={async () => {
            const response = await fetch("/import_raw_data", {
              method: "POST",
              headers: {
                "Content-Type": "application/json"
              },
              body: JSON.stringify(file)
            });

            if (response.ok) {
              console.log("response worked!");
            }
          }}
        >
          IMPORT CSV
        </button></td>
        </table>
      </form>
      <li>
      <Link to="/graph-view"> GO TO Graph View</Link>
      </li>

      <br />

      <table>
        <thead>
          <tr key={"header"}>
            {headerKeys.map((key) => (
              <th>{key}</th>
            ))}
          </tr>
        </thead>

        <tbody>
          {array.map((item) => (
            <tr key={item.id}>
              {Object.values(item).map((val) => (
                <td>{val}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}


export default ImportPage