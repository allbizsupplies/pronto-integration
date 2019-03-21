
class JSON {
  decode(jsonStr) {
    SC := ComObjCreate("ScriptControl") 
    SC.Language := "JScript"

    jsCode =
    (
    function arrangeForAhkTraversing(obj) {
      if(obj instanceof Array) {
        for(var i=0 ; i<obj.length ; ++i)
          obj[i] = arrangeForAhkTraversing(obj[i]) ;
        return ['array',obj] ;
      } else if(obj instanceof Object) {
        var keys = [], values = [] ;
        for(var key in obj) {
          keys.push(key) ;
          values.push(arrangeForAhkTraversing(obj[key])) ;
        }
        return ['object',[keys,values]] ;
      } else
        return [typeof obj,obj] ;
    }
    )

    SC.ExecuteStatement(jsCode "; obj=" jsonStr)
    return this.convertJSONtoAHK(SC.Eval("arrangeForAhkTraversing(obj)"))
  }

  convertJSONtoAHK(jsObj) {
    if (jsObj[0] = "object") {
      obj := {}, keys := jsObj[1][0], values := jsObj[1][1]
      loop % keys.length
        obj[keys[A_Index-1]] := this.convertJSONtoAHK(values[A_Index-1])
      return obj
    } 
    else if (jsObj[0] = "array") {
      array := []
      loop % jsObj[1].length
        array.Insert(this.convertJSONtoAHK(jsObj[1][A_Index-1]))
      return array
    } 
    else return jsObj[1]
  }
}
