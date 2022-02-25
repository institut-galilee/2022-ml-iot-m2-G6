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
    // > Pour CameraX
    private lateinit var binding : ActivityHeadBinding
    private lateinit var cameraExecutor : ExecutorService
    private var imageCapture : ImageCapture? = null
    // > Pour GRPC
    private lateinit var timer : Timer
    // > Pour accéléromètre
    private lateinit var sensorManager: SensorManager
    private lateinit var accel : Sensor

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityHeadBinding.inflate(layoutInflater)
        setContentView(binding.root)

        /* ************************************************************** */
        /* ************* Auteur DEBUT : Hajar BOUZIANE ****************** */
        // On initialise un timer pour exécuter une fonction toutes les x secondes
        timer = Timer()

        // on lance la caméra
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

        // Button pour quitter la réunion
        val butQT = findViewById<Button>(R.id.btn_quitterT)
        butQT.setOnClickListener {
            // On dit au serveur que la réunion est terminé
            etatReu = "termine"
            connexionServer()
            // on réinitialise les variables globals
            nomReu = ""
            mailEtud =""
            optionTeteOuMain = ""
            etatReu = ""
            // on arrête le timer
            timer.cancel()
            // on arrêtre l'accéléromètre
            sensorManager.unregisterListener(this)
            // on est rediriger vers la page d'acceuil
            startActivity(Intent(this, AcceuilActivity::class.java));
        }

        // Button pour commencer la réunion
        val butST = findViewById<Button>(R.id.btn_startT)
        butST.setOnClickListener {
            connectHead = "true"
            optionTeteOuMain = "tete"
            // On précise au serveur que la réunion sur la tête est en cours
            etatReu = "en cours"
            //on initialise l'accéléromètre
            sensorManager = getSystemService(SENSOR_SERVICE) as SensorManager
            accel = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
            // les données sont envoyés à la vitesse SENSOR_DELAY_NORMAL
            sensorManager.registerListener(this,accel, SensorManager.SENSOR_DELAY_NORMAL)

            //On envoie les données au serveur toutes les 2 secondes (accéléromètre et image entre autres)
            timer.schedule(object : TimerTask() {
                override fun run() {
                    connexionServer()
                }
            }, 0, 2000)
        }
        /* *************** Auteur FIN : Hajar BOUZIANE ****************** */
        /* ************************************************************** */

    }

    // ImageProxy -> Bitmap : https://stackoverflow.com/questions/70164601/android-camerax-image-capture-onimagesaved-never-runs#:~:text=private%20fun%20imageProxyToBitmap(image%3A%20ImageProxy)%3A%20Bitmap%20%7B%0A%20%20%20%20val%20planeProxy%20%3D%20image.planes%5B0%5D%0A%20%20%20%20val%20buffer%3A%20ByteBuffer%20%3D%20planeProxy.buffer%0A%20%20%20%20val%20bytes%20%3D%20ByteArray(buffer.remaining())%0A%20%20%20%20buffer.get(bytes)%0A%20%20%20%20return%20BitmapFactory.decodeByteArray(bytes%2C%200%2C%20bytes.size)%0A%7D
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

    // Prendre une photo : https://stackoverflow.com/questions/70164601/android-camerax-image-capture-onimagesaved-never-runs#:~:text=imageCapture.takePicture(ContextCompat.getMainExecutor(requireContext())%2Cobject%20%3A%0A%20%20%20%20%20%20%20%20ImageCapture.OnImageCapturedCallback()%20%7B%0A%20%20%20%20%20%20%20%20override%20fun%20onCaptureSuccess(image%3A%20ImageProxy)%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20super.onCaptureSuccess(image)%0A%20%20%20%20%20%20%20%20%20%20%20%20val%20bitmap%20%3DimageProxyToBitmap(image)
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

    //Démarrer la caméra : https://www.youtube.com/watch?v=HjXJh_vHXFs
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

            val cameraSelector = CameraSelector.DEFAULT_FRONT_CAMERA
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

    //Permission : https://www.youtube.com/watch?v=HjXJh_vHXFs
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

    //Permission : https://www.youtube.com/watch?v=HjXJh_vHXFs
    private fun allPermissionGranted() =
        Constants.REQUIRED_PERMISSIONS.all {
            ContextCompat.checkSelfPermission(
                baseContext, it
            ) == PackageManager.PERMISSION_GRANTED
        }


    // Vidéo : https://www.youtube.com/watch?v=qChiiARAcsI
    override fun onSensorChanged(event: SensorEvent?) {
        if(event?.sensor?.type == Sensor.TYPE_ACCELEROMETER){
            x = event.values[0]
            y = event.values[1]
            z = event.values[2]
            takePhoto()
        }
    }

    // Vidéo : https://www.youtube.com/watch?v=qChiiARAcsI
    override fun onAccuracyChanged(p0: Sensor?, p1: Int) {
        return
    }

    override fun onBackPressed() {
        Toast.makeText(this, "Appuyer sur QUITTER pour sortir de la réunion", Toast.LENGTH_SHORT).show()
    }
}