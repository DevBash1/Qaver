let r = new req();

r.send("/server.py",{
    type: "POST",
    params: "number=50",
    success: function(res){
        console.log(res)
    },
    error: function(res){
        console.log(res)
    }
})

function upload() {
    var a = document.createElement("input");
    a.type = "file";
    a.accept = "*";
    a.name = "file";
    a.id = "file";
    a.style = "visibility:hidden";
    a.multiple = "true";
    document.body.appendChild(a);

    a.addEventListener('change', function(e) {
        
        let len = this.files.length;

        var fd = new FormData();
        for(i=0;i<len;i++){
            var file = this.files[i];
            fd.append("file"+(i+1), file);
        }
        fd.append("id", "1");

        var xhr = new XMLHttpRequest();
        xhr.open('POST', 'server.py', true);

        xhr.upload.onprogress = function(e) {
            if (e.lengthComputable) {
                var percentComplete = (e.loaded / e.total) * 100;
                console.log(percentComplete + '% uploaded');
            }
        }
        ;

        xhr.onload = function() {
            if (this.status == 200) {
                var resp = this.response;
                let song = document.createElement("audio");
                song.src = resp;
                song.play();
                document.body.appendChild(song)
                console.log('Server got:', resp);
                
            } else {
                console.log("Error")
            }
        }

        xhr.send(fd);
    }, false);

    a.click();
}
setTimeout(function(){
    //upload()
},1000)

<?python
print("console.log('Coming From Python')")
?>