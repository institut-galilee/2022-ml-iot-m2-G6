package com.example.appspycheat

import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.os.Bundle
import android.util.Base64
import android.util.Log
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.example.appspycheat.databinding.ActivityHeadBinding
import java.io.ByteArrayOutputStream
import java.nio.ByteBuffer
import java.util.*
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

class HeadActivity : AppCompatActivity(), SensorEventListener {
    private lateinit var binding : ActivityHeadBinding
    private lateinit var cameraExecutor : ExecutorService
    private var imageCapture : ImageCapture? = null
    private lateinit var timer : Timer

    private lateinit var sensorManager: SensorManager
    private lateinit var accel : Sensor

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityHeadBinding.inflate(layoutInflater)
        setContentView(binding.root)

        timer = Timer()

        optionTeteOuMain = "main"

        if (allPermissionGranted()) {
            Toast.makeText(this,
                "We Have Permission",
                Toast.LENGTH_SHORT).show()
            startCamera()
        }else{
            ActivityCompat.requestPermissions(
                this, Constants.REQUIRED_PERMISSIONS,
                Constants.REQUEST_CODE_PERMISSION
            )
        }
        cameraExecutor = Executors.newSingleThreadExecutor()


        val butQT = findViewById<Button>(R.id.btn_quitterT)
        butQT.setOnClickListener {
            nomReu = ""
            mailEtud =""
            optionTeteOuMain = ""
            tenteConnexion = "false"
            timer.cancel()
            sensorManager.unregisterListener(this)
            startActivity(Intent(this, AcceuilActivity::class.java));
        }
        val butST = findViewById<Button>(R.id.btn_startT)
        butST.setOnClickListener {
            connectHead = "true"
            sensorManager = getSystemService(SENSOR_SERVICE) as SensorManager
            accel = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
            sensorManager.registerListener(this,accel, SensorManager.SENSOR_DELAY_NORMAL)
            timer.schedule(object : TimerTask() {
                override fun run() {
                    connexionServer()
                }
            }, 0, 2000)
        }
    }

    // ImageProxy -> Bitmap
    private fun imageProxyToBitmap (image: ImageProxy): Bitmap {
        val planeProxy = image.planes[0]
        val buffer: ByteBuffer = planeProxy.buffer
        val bytes = ByteArray(buffer.remaining())
        buffer.get(bytes)

        return BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
    }

    // Bitmap -> String Base64
    private fun encodeImage(bm: Bitmap): String? {
        val baos = ByteArrayOutputStream()
        bm.compress(Bitmap.CompressFormat.JPEG, 16, baos)
        val b = baos.toByteArray()
        return Base64.encodeToString(b, Base64.NO_WRAP)
    }

    private fun takePhoto(){
        val imageCapture = imageCapture ?: return
        imageCapture.takePicture(cameraExecutor, object :
            ImageCapture.OnImageCapturedCallback() {
            override fun onCaptureSuccess(image: ImageProxy) {
                // From ImageProxy To Bitmap
                val bitmap = imageProxyToBitmap(image)
                // From Bitmap to String Base64
                val imageStr = encodeImage(bitmap)
                println(imageStr.toString())
                imageForGRPC = imageStr.toString()
                image.close()
            }
            override fun onError(exception: ImageCaptureException) {
                super.onError(exception)
            }
        })
    }


    private fun startCamera(){
        val cameraProviderFuture = ProcessCameraProvider.getInstance(this)

        cameraProviderFuture.addListener({

            val cameraProvider : ProcessCameraProvider = cameraProviderFuture.get()
            val preview = Preview.Builder().build().also { mPreview ->
                mPreview.setSurfaceProvider(
                    binding.previewView.surfaceProvider
                )
            }

            imageCapture = ImageCapture.Builder().build()

            val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
            try {
                cameraProvider.unbindAll()
                cameraProvider.bindToLifecycle(
                    this, cameraSelector,
                    preview, imageCapture
                )
            }catch(e: Exception){
                Log.d(Constants.TAG, "startCamera Fail: ",e)
            }
        }, ContextCompat.getMainExecutor(this))

    }


    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if(requestCode == Constants.REQUEST_CODE_PERMISSION){
            if(allPermissionGranted()){
                startCamera()
            }else{
                Toast.makeText(this,
                    "Permissions not granted by the user.",
                    Toast.LENGTH_SHORT).show()
                finish()
            }
        }
    }

    private fun allPermissionGranted() =
        Constants.REQUIRED_PERMISSIONS.all {
            ContextCompat.checkSelfPermission(
                baseContext, it
            ) == PackageManager.PERMISSION_GRANTED
        }


    override fun onSensorChanged(event: SensorEvent?) {
        if(event?.sensor?.type == Sensor.TYPE_ACCELEROMETER){
            x = event.values[0]
            y = event.values[1]
            z = event.values[2]
            takePhoto()
        }
    }

    override fun onAccuracyChanged(p0: Sensor?, p1: Int) {
        return
    }
}