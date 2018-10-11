class Collector {
  /**
   * A handler class for receving and sending data to Server
   *
   * @access    public
   * @constructs DataHandler()
   *
   * @param serverAddress attributes   the server address that will interact with 
   *
   */

  constructor() {
    this.result = {};
    this.gl = this.getGL();
    this.result['gpuven'] = this.getGPUVen(this.gl);
    this.result['gpuren'] = this.getGPURen(this.gl);
    this.datahandler = new DataHandler('http://coding.songli.io/collector');
    var res = this.datahandler.updateDatabase(this.result);
    console.log(res);
  }

  getGL() {
    /**
     * create a canvas named canvas and return the gl of this canvas
     */
    var canvas = document.createElement('canvas');
    var gl = null;
    try {
      gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    } catch (e) { /* squelch */ }
    if (!gl) { gl = null; }
    return gl;
  }

  getGPUVen(gl) {
    var debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
    if (debugInfo) return gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
    return "No Debug Info";
  }

  getGPURen(gl) {
    var debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
    if (debugInfo) return gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
    return "No Debug Info";
  }

}
