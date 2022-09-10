// #include "autoCorrect.h"
#include <iostream>
#include <cmath>

void autoCorrect(double* input,int inputLength,double acc,int prc){
    //复制数组 input
    double* inputCopy = new double[inputLength];
    for(int i=0;i<inputLength;i++){
        inputCopy[i] = input[i];
    }
    //存储第一项
    double first = inputCopy[0];

    //计算数组 inputCopy 的变化量, 顺便省略prc位后的小数
    int* inputCopyDiff = new int[inputLength];
    inputCopyDiff[0] = 0;
    for(int i=1;i<inputLength;i++){
        inputCopyDiff[i] = inputCopy[i]*pow(10,prc) - inputCopy[i-1]*pow(10,prc);
    }

    // //储存误差
    // int error = 0;

    //储存步长 step 和当前走了多少步 stepCount
    int step = inputCopyDiff[1];
    int stepCount = 1;

    //遍历数组 inputCopyDiff
    for(int i=2;i<inputLength;i++){
        if(inputCopyDiff[i]>=step-acc&&inputCopyDiff[i]<=step+acc){
            //步长和+-误差差不多的算到一块, 然后去平均值
            step=(step*stepCount+inputCopyDiff[i])/(stepCount+1);
            stepCount++;
            for(int j = i-stepCount+1;j<i;j++){
                //然后把这一块的值都改成平均值
                inputCopyDiff[j] = step;
            }
        }
        else{
            int temp=step;
            //不然就重新设置步长
            step = inputCopyDiff[i];
            inputCopyDiff[i] = temp;
            stepCount = 1;
        }
    }






    //将变化量数组 inputCopyDiff 复制到数组 input 里
    for(int i=0;i<inputLength;i++){
        input[i] = inputCopyDiff[i];//pow(10,prc);
    }

}


int main(){
    double input[50]={1.959, 2.497, 2.991, 3.508, 4.015, 4.548, 5.031, 5.554, 6.05, 6.516, 7.018, 7.506, 7.999, 8.537, 9.033, 9.541, 10.039, 10.304, 10.557, 10.822, 11.072, 11.311, 11.555, 11.819, 12.071, 12.341, 12.621, 12.862, 13.107, 13.325, 13.549, 13.798, 14.154, 14.372, 14.613, 14.822, 15.038, 15.318, 15.57, 15.816, 16.065, 16.319, 16.562, 16.79, 17.018, 17.273, 17.521, 17.809};
    autoCorrect(input,50,10,2);

    return 0;
}