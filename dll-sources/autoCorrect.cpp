#include <cmath>
#include <cstring>
#include <iostream>

extern "C" void autoCorrect(int inputLength, double *input,
                            double maxVariance) {
    // 计算 input 的差分数组
    double *inputDiff = new double[inputLength];
    for (int i = 1; i < inputLength; i++)
        inputDiff[i] = input[i] - input[i - 1];

    // 储存平均步长、上一步平均步长、加权和、平方和、当前步数
    // 加权平均数 x=Σixi/Σi=Σixi/[i(i+1)/2]
    // 方差 s²=Σ(xi-x)/n=(Σxi²-2xΣxi+nx²)/n=Σxi²/n-x²
    double avgStep = inputDiff[1], lastStep = avgStep, weightedSum = avgStep,
           squareSum = pow(avgStep, 2);
    int stepCount = 1;

    // 遍历数组 inputDiff
    for (int i = 2; i < inputLength; i++) {
        squareSum += pow(inputDiff[i], 2);
        weightedSum += ++stepCount * inputDiff[i];
        avgStep = weightedSum / (stepCount * (stepCount + 1) / 2);
        double variance = squareSum / stepCount - pow(avgStep, 2);
        if (variance <= maxVariance)
            // 方差在可容许范围内的作为一组取平均值
            lastStep = avgStep;
        else {
            // 把上一组的值都改成平均值
            for (int j = i - stepCount + 1; j < i; j++)
                inputDiff[j] = lastStep;
            // 重新设置步长
            avgStep = lastStep = weightedSum = inputDiff[i];
            squareSum = pow(avgStep, 2);
            stepCount = 1;
        }
    }
    for (int i = inputLength - stepCount; i < inputLength; i++)
        // 把最后一组的值都改成平均值
        inputDiff[i] = avgStep;

    // 将新数组微调后复制到原数组
    for (int i = 1; i < inputLength; i++)
        input[i] = input[i - 1] + inputDiff[i];
}