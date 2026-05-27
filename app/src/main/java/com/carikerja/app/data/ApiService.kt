package com.carikerja.app.data

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.GET
import retrofit2.http.Query

interface JobApiService {
    @GET("jobs")
    suspend fun getOverseasJobs(
        @Query("country") country: String = "Global"
    ): List<Job>
}

object RetrofitClient {
    private const val BASE_URL = "https://api.example.com/" // Ganti dengan API lowongan kerja nyata

    val apiService: JobApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(JobApiService::class.java)
    }
}
