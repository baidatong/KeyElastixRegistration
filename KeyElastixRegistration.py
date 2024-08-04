# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.uix.button import Button
from kivy.graphics.texture import Texture
from kivy.uix.slider import Slider
from kivy.uix.screenmanager import ScreenManager, Screen
import kivy.garden
from kivy.uix.label import Label

from kivy.uix.floatlayout import FloatLayout
from kivy.metrics import Metrics
import SimpleITK as sitk
import numpy as np
from myimage import MyImage

from file_choose import Filechooser



class ButtonTest(FloatLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.button01 = Button(text='next',
                               font_size = 30,
                               size=["100dp","50dp"],
                               size_hint = [None,None],
                               #state = 'down',
                               pos = ["0dp","0dp"])

        self.button02 = Button(text='Select Point',
                               font_size=30,
                               size=["100dp","50dp"],
                               size_hint = [None,None],
                               pos = ["200dp","0dp"])
        self.file_path = None
        self.add_widget(self.button01)
        self.add_widget(self.button02)
        self.ud_group_record = None
        self.record = None
        self.record2 = None
        self.record2_num = []
    def load_image(self):
        image = sitk.ReadImage(self.file_path[0])
        self.nii_image = image
        rescale_image = sitk.RescaleIntensity(image, 0, 255)
        self.buf0 = sitk.GetArrayFromImage(rescale_image)
        self.slide_control = Slider(min=0, max=self.buf0.shape[0]-1,value = 0,orientation='vertical',value_track=True,pos = ["500dp","200dp"],size=["100dp","300dp"],
                               size_hint = [None,None])
        self.slide_control.bind(value = self.on_value)
        self.add_widget(self.slide_control)
        #self.window = Window
        # self.add_widget(self.button02)
    def on_value(self,instance,num):
        self.show_image(self.buf0,np.round(num).astype(np.int16))
        if self.record2 is not None:
            if self.record2['num'] == np.round(num):
                self.image.plot_select(self.record2)
        if self.record is not None:
            if self.record['num'] == np.round(num):
                self.image.plot_select(self.record)
    def show_image(self,buf,num):
        buf0 =buf[num,:,:]
        buf1 = np.flip(buf0,0)
        buf1= buf1.astype('uint8')
        w,h = buf1.shape
        self.num = num
        texture =  Texture.create(size=(h ,w),  colorfmt='luminance')
        texture.blit_buffer(buf1.flatten(), colorfmt='luminance', bufferfmt='ubyte')
        self.image = MyImage(pos=["0dp","100dp"], size_hint = [None,None],size=(h, w), texture=texture)
        self.add_widget(self.image)
        self.button01.bind(on_press = self.set_next_sm)
        self.button02.bind(on_press = self.get_coordinates)
        return self
    def get_coordinates(self,instance):
        #print(self.image.coordinates_select)
        if self.image.pre_touch is None:
            return
        if instance.text=="Select Point":
            if self.record2 is not None:
                self.image.del_select(self.record2)
            self.record2 = dict()
            self.record2['pre_touch'] = self.image.pre_touch
            ori = self.image.pos
            print("x,y:")
            print(self.image.pre_touch.x-ori[0])
            print(self.image.pre_touch.y-ori[1])

            self.record2['ud_group_record'] = self.image.pre_ud
            self.record2['group'] = 'record_group2'
            self.record2['num'] = self.num
            self.record_volume(self.nii_image,self.record2,ori)
            self.image.plot_select(self.record2)
        return self
    def set_next_sm(self,instance):
        if instance.text=="next":
            if self.next_sm != "None":
                App.get_running_app().sm.current = self.next_sm
                App.get_running_app().sm_all[self.next_sm].open_pop_up()
        else:
            print("start registration")
            print(App.get_running_app().record_reg_re)
            record1 = App.get_running_app().record_reg_re['show_image']
            record2 = App.get_running_app().record_reg_re['show_image2']
            im1 = record1['img']
            coord1 = np.array(record1['coord'])
            shape1 = np.array(im1.GetSize())
            space1 = np.array(im1.GetSpacing())
            l1 = (coord1 -1)*space1
            m1 = (shape1 - coord1)*space1

            im2 = record2['img']
            coord2 = np.array(record2['coord'])
            shape2 = np.array(im2.GetSize())
            space2 = np.array(im2.GetSpacing())
            l2 = (coord2 -1)*space2
            m2 = (shape2 - coord2)*space2

            maxl = np.minimum(l1,l2)
            minm = np.minimum(m1,m2)

            roi1_min = np.round(maxl/space1)
            roi1_max = np.round(minm/space1)
            start1 = (np.round(coord1 - roi1_min).astype(np.int32)).tolist()
            end1 = (np.round(coord1 + roi1_max).astype(np.int32)).tolist()
            crop1 = (shape1 - end1).tolist()
            crop = sitk.CropImageFilter()
            crop.SetLowerBoundaryCropSize([start1[0], crop1[1], start1[2]])
            crop.SetUpperBoundaryCropSize([crop1[0], start1[1], crop1[2]])
            cropped_image = crop.Execute(im1)
            sitk.WriteImage(cropped_image, '001.nii.gz')

            roi2_min = np.round(maxl/space2)
            roi2_max = np.round(minm / space2)
            start2 = (np.round(coord2 - roi2_min).astype(np.int32)).tolist()
            end2 = (np.round(coord2 + roi2_max).astype(np.int32)).tolist()
            crop2 = (shape2 - end2).tolist()
            #shape2 = shape2.tolist()
            crop1x = sitk.CropImageFilter()
            crop1x.SetLowerBoundaryCropSize([start2[0],crop2[1],start2[2]])
            crop1x.SetUpperBoundaryCropSize([crop2[0], start2[1],crop2[2]])
            cropped_imagex = crop1x.Execute(im2)
            sitk.WriteImage(cropped_imagex, '002.nii.gz')

            elastixImageFilter = sitk.ElastixImageFilter()
            elastixImageFilter.SetFixedImage(cropped_image)
            elastixImageFilter.SetMovingImage(cropped_imagex)
            parameterMap = sitk.GetDefaultParameterMap('rigid')
            #
            parameterMap['FixedInternalImagePixelType'] = ['float']
            parameterMap['MovingInternalImagePixelType'] = ['float']

            parameterMap['Registration'] = ['MultiResolutionRegistration']
            parameterMap['Interpolator'] = ['BSplineInterpolator']
            parameterMap['ResampleInterpolator'] = ['FinalBSplineInterpolator']
            parameterMap['Resampler'] = ['DefaultResampler']
            parameterMap['FixedImagePyramid'] = ['FixedSmoothingImagePyramid']
            parameterMap['MovingImagePyramid'] = ['MovingSmoothingImagePyramid']

            parameterMap['Transform'] = ['EulerTransform']
            parameterMap['Optimizer'] = ['AdaptiveStochasticGradientDescent']
            parameterMap['Metric'] = ['AdvancedMattesMutualInformation']

            parameterMap['NumberOfHistogramBins'] = ['64']

            parameterMap['NumberOfResolutions'] = ['3']
            parameterMap['ImagePyramidSchedule'] = ['8 8 2  4 4 1  1 1 1']

            parameterMap['AutomaticScalesEstimation'] = ['true']
            parameterMap['AutomaticTransformInitialization'] = ['true']
            parameterMap['HowToCombineTransforms'] = ['Compose']

            parameterMap['MaximumNumberOfIterations'] = ['2000']
            # parameterMap['UseRandomSampleRegion'] = ['true']
            parameterMap['MaximumStepLength'] = ['1']
            parameterMap['RequiredRatioOfValidSamples'] = ['0.05']

            parameterMap['NumberOfSpatialSamples'] = ['2000']
            parameterMap['NewSamplesEveryIteration'] = ['true']
            parameterMap['ImageSampler'] = ['Random']

            parameterMap['BSplineInterpolationOrder'] = ['1']
            parameterMap['FinalBSplineInterpolationOrder'] = ['3']

            elastixImageFilter.SetParameterMap(parameterMap)
            resultImage = elastixImageFilter.Execute()
            sitk.WriteImage(resultImage, 'temp_result.nii.gz')

            transformParameterMap = elastixImageFilter.GetTransformParameterMap()
            p1 = transformParameterMap[0]
            ori = p1['Origin']
            eulerangle = np.array(np.double(p1['TransformParameters'][:3]))
            trans = np.array(np.double(p1['TransformParameters'][3:]))
            center = np.array(np.double(p1['CenterOfRotationPoint']))
            rigid_euler = sitk.Euler3DTransform(center, eulerangle[0], eulerangle[1], eulerangle[2], trans)

            extreme_points = [
                im2.TransformIndexToPhysicalPoint((0, 0, 0)),
                im2.TransformIndexToPhysicalPoint((im2.GetWidth(), 0, 0)),
                im2.TransformIndexToPhysicalPoint((im2.GetWidth(), im2.GetHeight(), 0)),
                im2.TransformIndexToPhysicalPoint((0, im2.GetHeight(), 0)),
                im2.TransformIndexToPhysicalPoint((0, 0, 0)),
                im2.TransformIndexToPhysicalPoint((im2.GetWidth(), 0, im2.GetDepth())),
                im2.TransformIndexToPhysicalPoint((im2.GetWidth(), im2.GetHeight(), im2.GetDepth())),
                im2.TransformIndexToPhysicalPoint((0, im2.GetHeight(), im2.GetDepth()))
            ]
            inv_euler2d = rigid_euler.GetInverse()

            extreme_points_transformed = [inv_euler2d.TransformPoint(pnt) for pnt in extreme_points]

            extreme_points_transformed = [inv_euler2d.TransformPoint(pnt) for pnt in extreme_points]
            min_x = min(extreme_points_transformed)[0]
            min_y = min(extreme_points_transformed, key=lambda p: p[1])[1]
            min_z = min(extreme_points_transformed, key=lambda p: p[2])[2]

            max_x = max(extreme_points_transformed)[0]
            max_y = max(extreme_points_transformed, key=lambda p: p[1])[1]
            max_z = max(extreme_points_transformed, key=lambda p: p[2])[2]
            output_spacing = im2.GetSpacing()
            output_direction = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
            output_origin = [min_x, min_y, min_z]

            output_size = [
                int((max_x - min_x) / output_spacing[0]),
                int((max_y - min_y) / output_spacing[1]),
                int((max_z - min_z) / output_spacing[2])
            ]
            resampled_image = sitk.Resample(
                im2,
                output_size,
                rigid_euler,
                sitk.sitkLinear,
                output_origin,
                output_spacing,
                output_direction,
            )

            sitk.WriteImage(resampled_image, 'final_result.nii.gz')



            #self.button01.text = 'Start Reg'
    def get_next_sm(self,next_sm):
        self.next_sm = next_sm
        if self.next_sm == "None":
            self.button01.text = 'Start Reg'

    def record_volume(self,img,record,ori):
        touch = record['pre_touch']
        x = (np.round(touch.x - ori[0])).astype('uint32').tolist()
        y = (np.round(touch.y - ori[1])).astype('uint32').tolist()
        z = np.asarray(record['num'],dtype=np.uint32).tolist()
        shape = img.GetSize() # num w h
        record = dict()
        record['img'] = img
        record['coord'] = [x,y,z]
        current_sm =  App.get_running_app().sm.current

        print()
        App.get_running_app().record_reg_re[current_sm] = record
        print(App.get_running_app().record_reg_re[current_sm])


#         x_left = x-1
#         x_right = shape[1] - x
#         y_up = y - 1
#         y_down = shape[2] - y
#         z_hip =  z -1
#         z_down = shape[0] -z
#         print(shape)
#         print([x,y,z])
#         # print([x_left,x_right,y_up,y_down,z_hip,z_down])
#         crop = sitk.CropImageFilter()
# # # right down
#         crop.SetLowerBoundaryCropSize([ x, 0, 0])
#         crop.SetUpperBoundaryCropSize([0,shape[1]-y, 0])
# #         # left upper
# #         crop.SetLowerBoundaryCropSize([0, 0, 0])
# #         crop.SetUpperBoundaryCropSize([shape[0]-x, shape[1]-y, 0])
#         cropped_image = crop.Execute(img)
#         sitk.WriteImage(cropped_image, 'test_crop002.nii.gz')

import sys

class Load_Screen(Screen):   #sm2
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def get_next(self,next_sm):
        self.Load_Screen02 =  Filechooser()
        self.Load_Screen02.get_next_sm(next_sm = next_sm)
        self.add_widget(self.Load_Screen02)
    def open_pop_up(self):
        self.Load_Screen02.open_Popup()

class RegScreen(Screen):     #sm1
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def get_next(self,next_sm):
        self.RegScreen01 = ButtonTest()
        self.RegScreen01.get_next_sm(next_sm = next_sm)
        self.add_widget(self.RegScreen01)

class ButtonTestApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.sm_all = dict()
        self.record_reg_ref = dict()

        name1 = 'pick_filename'
        name2 = 'show_image'
        name3 = 'pick_filename2'
        name4 = 'show_image2'

        self.sm_all[name1] = Load_Screen(name=name1)
        self.sm_all[name2] = RegScreen(name=name2)
        self.sm_all[name3] = Load_Screen(name=name3)
        self.sm_all[name1].get_next(name2)


        self.sm_all[name2].get_next(name3)


        self.sm_all[name3].get_next(name4)

        self.sm_all[name4] = RegScreen(name=name4)
        self.sm_all[name4].get_next('None')

        self.sm.add_widget(self.sm_all[name1])
        self.sm.add_widget(self.sm_all[name2])
        self.sm.add_widget(self.sm_all[name3])
        self.sm.add_widget(self.sm_all[name4])
        self.record_reg_re = dict()
        self.sm.current = name1
        self.sm_all[name1].open_pop_up()
        #sm.current = 'show_image'
        return self.sm

if __name__ == '__main__':
    ButtonTestApp().run()