export PATH=/usr/local/cuda-10.0/bin${PATH:+:${PATH}}
./darknet detector train axe/obj.data axe/yolo-obj_labo_axe.cfg darknet53.conv.74 -map

export PATH=/usr/local/cuda-10.0/bin${PATH:+:${PATH}}
./darknet detector demo axe/obj.data axe/yolov3-obj_3l_labo_axe.cfg axe/backup/yolov3-tiny_30000.weights axe/semaphore.avi -i 0 -thresh 0.25 -output axe/res_semaphore.avi


./darknet detector test axe/obj.data  axe/yolov3-obj_3l_labo_axe.cfg axe/backup/yolov3-tiny_30000.weights axe/shot_36_space.jpg

export PATH=/usr/local/cuda-10.0/bin${PATH:+:${PATH}}
./darknet detector demo axe/obj.data axe/yolov3-obj_3l_labo_axe.cfg axe/backup/yolov3-tiny_30000.weights -thresh 0.25 -c 0
