import React, { useState, useEffect } from 'react'
import { assets } from '../assets/assets' // Ensure this points to a valid upload icon

const MyProfile = () => {
  const [isEdit, setIsEdit] = useState(false)
  const [image, setImage] = useState(null)
  const [userData, setUserData] = useState(null)

  // Load dummy user data
  useEffect(() => {
    setUserData({
      name: 'John Doe',
      email: 'john@example.com',
      phone: '9876543210',
      gender: 'Male',
      dob: '1995-08-25',
      image: assets.profile_pic,
      address: {
        line1: '123 Street Name',
        line2: 'City, Country',
      },
    })
  }, [])

  const updateUserProfileData = () => {
    alert('Profile updated (not really, this is just frontend only!)')
    setIsEdit(false)
    setImage(null)
  }

  return userData ? (
    <div className='max-w-lg flex flex-col gap-2 text-sm pt-5'>

      {/* Profile Image Upload */}
      {isEdit ? (
        <label htmlFor='image'>
          <div className='inline-block relative cursor-pointer'>
            <img
              className='w-36 rounded opacity-75'
              src={image ? URL.createObjectURL(image) : userData.image}
              alt='profile'
            />
            <img
              className='w-10 absolute bottom-12 right-12'
              src={image ? '' : assets.upload_icon}
              alt='upload'
            />
          </div>
          <input
            onChange={(e) => setImage(e.target.files[0])}
            type='file'
            id='image'
            hidden
          />
        </label>
      ) : (
        <img className='w-36 rounded' src={userData.image} alt='profile' />
      )}

      {/* Name Field */}
      {isEdit ? (
        <input
          className='bg-gray-50 text-3xl font-medium max-w-60'
          type='text'
          value={userData.name || ''}
          onChange={(e) => setUserData(prev => ({ ...prev, name: e.target.value }))}
        />
      ) : (
        <p className='font-medium text-3xl text-[#262626] mt-4'>
          {userData.name}
        </p>
      )}

      <hr className='bg-[#ADADAD] h-[1px] border-none' />

      {/* Contact Info */}
      <div>
        <p className='text-gray-600 underline mt-3'>CONTACT INFORMATION</p>
        <div className='grid grid-cols-[1fr_3fr] gap-y-2.5 mt-3 text-[#363636]'>
          <p className='font-medium'>Email id:</p>
          <p className='text-blue-500'>{userData.email}</p>

          <p className='font-medium'>Phone:</p>
          {isEdit ? (
            <input
              className='bg-gray-50 max-w-52'
              type='text'
              value={userData.phone || ''}
              onChange={(e) =>
                setUserData(prev => ({ ...prev, phone: e.target.value }))
              }
            />
          ) : (
            <p className='text-blue-500'>{userData.phone}</p>
          )}

          <p className='font-medium'>Address:</p>
          {isEdit ? (
            <div className='flex flex-col gap-1'>
              <input
                className='bg-gray-50'
                type='text'
                value={userData.address?.line1 || ''}
                onChange={(e) =>
                  setUserData(prev => ({
                    ...prev,
                    address: {
                      ...prev.address,
                      line1: e.target.value,
                    },
                  }))
                }
              />
              <input
                className='bg-gray-50'
                type='text'
                value={userData.address?.line2 || ''}
                onChange={(e) =>
                  setUserData(prev => ({
                    ...prev,
                    address: {
                      ...prev.address,
                      line2: e.target.value,
                    },
                  }))
                }
              />
            </div>
          ) : (
            <p className='text-gray-500'>
              {userData.address?.line1} <br /> {userData.address?.line2}
            </p>
          )}
        </div>
      </div>

      {/* Basic Info */}
      <div>
        <p className='text-[#797979] underline mt-3'>BASIC INFORMATION</p>
        <div className='grid grid-cols-[1fr_3fr] gap-y-2.5 mt-3 text-gray-600'>
          <p className='font-medium'>Gender:</p>
          {isEdit ? (
            <select
              className='max-w-20 bg-gray-50'
              value={userData.gender || 'Not Selected'}
              onChange={(e) =>
                setUserData(prev => ({ ...prev, gender: e.target.value }))
              }
            >
              <option value='Not Selected'>Not Selected</option>
              <option value='Male'>Male</option>
              <option value='Female'>Female</option>
            </select>
          ) : (
            <p className='text-gray-500'>{userData.gender}</p>
          )}

          <p className='font-medium'>Birthday:</p>
          {isEdit ? (
            <input
              className='max-w-28 bg-gray-50'
              type='date'
              value={userData.dob || ''}
              onChange={(e) =>
                setUserData(prev => ({ ...prev, dob: e.target.value }))
              }
            />
          ) : (
            <p className='text-gray-500'>{userData.dob}</p>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className='mt-10'>
        {isEdit ? (
          <button
            onClick={updateUserProfileData}
            className='border border-primary px-8 py-2 rounded-full hover:bg-primary hover:text-white transition-all'
          >
            Save information
          </button>
        ) : (
          <button
            onClick={() => setIsEdit(true)}
            className='border border-primary px-8 py-2 rounded-full hover:bg-primary hover:text-white transition-all'
          >
            Edit
          </button>
        )}
      </div>
    </div>
  ) : null
}

export default MyProfile
