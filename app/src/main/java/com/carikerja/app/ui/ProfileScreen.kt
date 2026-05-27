package com.carikerja.app.ui

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import com.carikerja.app.data.UserProfile
import java.io.ByteArrayOutputStream

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    userProfile: UserProfile?,
    onSave: (UserProfile) -> Unit,
    onImageSelected: (ByteArray) -> Unit
) {
    val context = LocalContext.current
    var name by remember { mutableStateOf(userProfile?.name ?: "") }
    var education by remember { mutableStateOf(userProfile?.education ?: "") }
    var location by remember { mutableStateOf(userProfile?.preferredLocation ?: "Indonesia") }
    var selectedField by remember { mutableStateOf(userProfile?.field ?: "Umum") }
    var expanded by remember { mutableStateOf(false) }
    
    val fields = listOf("Umum", "Informatika", "Ekonomi", "Teknik", "Kesehatan", "Hukum", "Sosial & Politik", "Sastra & Budaya", "Pendidikan")

    val launcher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri?.let {
            val inputStream = context.contentResolver.openInputStream(it)
            val bitmap = BitmapFactory.decodeStream(inputStream)
            val outputStream = ByteArrayOutputStream()
            // Kompresi: Kualitas 70% untuk menghemat storage
            bitmap.compress(Bitmap.CompressFormat.JPEG, 70, outputStream)
            onImageSelected(outputStream.toByteArray())
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
            .verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Spacer(modifier = Modifier.height(32.dp))
        
        Box(
            modifier = Modifier
                .size(100.dp)
                .clickable { launcher.launch("image/*") }
        ) {
            if (userProfile?.profileImageUrl != null) {
                AsyncImage(
                    model = userProfile.profileImageUrl,
                    contentDescription = "Profile Picture",
                    modifier = Modifier
                        .fillMaxSize()
                        .clip(CircleShape),
                    contentScale = ContentScale.Crop
                )
            } else {
                Icon(
                    imageVector = Icons.Default.AccountCircle,
                    contentDescription = "Add Photo",
                    modifier = Modifier.fillMaxSize(),
                    tint = MaterialTheme.colorScheme.primary
                )
            }
            Surface(
                modifier = Modifier
                    .align(Alignment.BottomEnd)
                    .size(28.dp),
                shape = CircleShape,
                color = MaterialTheme.colorScheme.primaryContainer
            ) {
                Icon(
                    imageVector = Icons.Default.Add,
                    contentDescription = null,
                    modifier = Modifier.padding(4.dp),
                    tint = MaterialTheme.colorScheme.onPrimaryContainer
                )
            }
        }
        
        Text(
            text = if (userProfile == null) "Lengkapi Profil" else "Edit Profil", 
            style = MaterialTheme.typography.headlineLarge, 
            fontWeight = FontWeight.Bold
        )

        ProfileTextField(value = name, onValueChange = { name = it }, label = "Nama Lengkap", icon = Icons.Default.Person, placeholder = "Nama Anda")
        ProfileTextField(value = education, onValueChange = { education = it }, label = "Pendidikan Terakhir", icon = Icons.Default.School, placeholder = "Contoh: S1 Teknik")
        ProfileTextField(value = location, onValueChange = { location = it }, label = "Lokasi Pilihan", icon = Icons.Default.LocationOn, placeholder = "Contoh: Jakarta / Remote")

        // Bidang Kategori Dropdown
        ExposedDropdownMenuBox(
            expanded = expanded,
            onExpandedChange = { expanded = !expanded },
            modifier = Modifier.fillMaxWidth()
        ) {
            OutlinedTextField(
                value = selectedField,
                onValueChange = {},
                readOnly = true,
                label = { Text("Bidang Keahlian") },
                leadingIcon = { Icon(Icons.Default.Build, contentDescription = null) },
                trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded) },
                modifier = Modifier.menuAnchor(ExposedDropdownMenuAnchorType.PrimaryEditable, true).fillMaxWidth(),
                shape = MaterialTheme.shapes.medium
            )
            ExposedDropdownMenu(
                expanded = expanded,
                onDismissRequest = { expanded = false }
            ) {
                fields.forEach { field ->
                    DropdownMenuItem(
                        text = { Text(field) },
                        onClick = {
                            selectedField = field
                            expanded = false
                        }
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        Button(
            onClick = {
                if (name.isNotBlank()) {
                    onSave(UserProfile(
                        userId = userProfile?.userId ?: "", 
                        name = name, 
                        education = education,
                        field = selectedField,
                        preferredLocation = location,
                        profileImageUrl = userProfile?.profileImageUrl
                    ))
                }
            },
            modifier = Modifier.fillMaxWidth().height(56.dp),
            shape = MaterialTheme.shapes.medium
        ) {
            Text(if (userProfile == null) "Mulai Cari Kerja" else "Simpan Perubahan", style = MaterialTheme.typography.titleMedium)
        }
    }
}

@Composable
fun ProfileTextField(value: String, onValueChange: (String) -> Unit, label: String, icon: ImageVector, placeholder: String) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        label = { Text(label) },
        placeholder = { Text(placeholder) },
        leadingIcon = { Icon(imageVector = icon, contentDescription = null) },
        modifier = Modifier.fillMaxWidth(),
        singleLine = true,
        shape = MaterialTheme.shapes.medium
    )
}
