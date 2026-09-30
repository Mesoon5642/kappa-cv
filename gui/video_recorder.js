function begin_record(length, filename, device) {
    return new Promise((resolve) => {

        let recorder = new RecordRTC(device, {
            type: 'video',
            mimeType: 'video/webm;codecs=vp8,opus',
            timeSlice: 1000
        });

        recorder
            .setRecordingDuration(length * 1000)
            .onRecordingStopped(function () {
                getSeekableBlob(recorder.getBlob(), function(seekableBlob) {
                    invokeSaveAsDialog(seekableBlob, filename);
                    resolve(seekableBlob); 
                });
            });

        recorder.startRecording();
    });
}