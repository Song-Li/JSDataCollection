class DataHandler {
  /**
   * A handler class for receving and sending data to Server
   *
   * @access    public
   * @constructs DataHandler()
   *
   * @param serverAddress attributes   the server address that will interact with 
   *
   */

  constructor(serverAddress = "") {
    this.serverAddress = serverAddress;
    this.uniqueLabel = this.requestUniqueLabel();
  }

  requestUniqueLabel() {
    this.doSend('getUniqueLabel', {'get_key':'get_key'}, false);
  }

  doSend (appName, keyValuePairs, async = false, encoded = true) {
    /**
     * do send to the server.
     *
     * This function will send the key_value pairs with encoded URI to prevent the bugs
     * introduced by special chars
     *
     * @param appName string   the aim app name to handle this send event
     * @param keyValuePairs map   the key value pairs. Example: {key = value}
     * @param async boolean     async or not. If false, return when finished
     *
     * @return result string    the handle result returned from the server
     */

    var xhttp = new XMLHttpRequest();
    var url = `${this.serverAddress}/${appName}`;
    var data = JSON.stringify(keyValuePairs);

    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        var res = this.responseText;
        return res
      }
    };

    xhttp.open("POST", url, async);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    if(encoded){
      xhttp.send(encodeURI(data));
    } else {
      xhttp.send(data);
    }
  }

  storePicture(dataURL) {
    var data = "imageBase64=" + encodeURIComponent(dataURL); 
    return this.doSend('pictures', data, async = true)
  }

  updateDatabase(valueData) {
    valueData['uniqueLabel'] = this.uniqueLabel;
    appName = 'updateFeatures';
    var dataStr = JSON.stringify(valueData) 
    this.doSend(appName, dataStr)
  }
}
