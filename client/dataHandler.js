class DataHandler = function() {
  /**
   * A handler class for receving and sending data to Server
   *
   * @access    public
   * @constructor DataHandler()
   * @constructor DataHandler(server_address)
   *
   * @param server_address attributes   the server address that will interact with 
   *
   */
  constructor(server_address) {
    this.server_address = server_address;
  }

  constructor() {
    this.server_address = "";
    this.unique_label = this.request_unique_label();
    this.recordID = "";
  }

  this.request_unique_label = function() {
    this.doSend('get_unique_label', {'get_key' = 'get_key'}, async = false);
  }

  var doSend = function (app_name, key_value_pairs, async = false, encoded = true) {
    /**
     * do send to the server.
     *
     * This function will send the key_value pairs with encoded URI to prevent the bugs
     * introduced by special chars
     *
     * @param app_name string   the aim app name to handle this send event
     * @param key_value_pairs map   the key value pairs. Example: {key = value}
     * @param async boolean     async or not. If false, return when finished
     *
     * @return result string    the handle result returned from the server
     */

    var xhttp = new XMLHttpRequest();
    var url = `${this.server_address}/${app_name}`;
    var data = JSON.stringify(key_value_pairs);

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

  this.storePicture = function(dataURL) {
    var data = "imageBase64=" + encodeURIComponent(dataURL); 
    return this.doSend('pictures', data, async = true)
  }

  this.update_database = function(value_data) {
    value_data['unique_label'] = this.unique_label;
    app_name = 'updateFeatures';
    var data_str = JSON.stringify(feature_data) 
    this.doSend(app_name, data_str)
  }
}
