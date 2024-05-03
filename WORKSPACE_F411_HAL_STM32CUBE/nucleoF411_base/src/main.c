#include "stm32f4xx_hal_msp.h"
#include "stm32f4xx_hal_gpio.h"
#include "stm32f4xx_hal_tim.h"
#include "stm32f4xx_hal_uart.h"
#include "stm32f4xx_hal_i2c.h"
#include "leds.h"
#include "sw.h"
#include "lm75.h"
#include "stm32f4xx_hal.h"
#include "paj7620u2.h"
#define INIT_REG_ARRAY_SIZE (sizeof(initRegisterArray)/sizeof(initRegisterArray[0]))

TIM_HandleTypeDef htim3;
TIM_HandleTypeDef htim5;
UART_HandleTypeDef huart2;
I2C_HandleTypeDef hi2c1;
const uint8_t initRegisterArray[][2] = {
    // BANK 0
    {0xEF,0x00}, {0x37,0x07}, {0x38,0x17}, {0x39,0x06}, {0x42,0x01},
    {0x46,0x2D}, {0x47,0x0F}, {0x48,0x3C}, {0x49,0x00}, {0x4A,0x1E},
    {0x4C,0x20}, {0x51,0x10}, {0x5E,0x10}, {0x60,0x27}, {0x80,0x42},
    {0x81,0x44}, {0x82,0x04}, {0x8B,0x01}, {0x90,0x06}, {0x95,0x0A},
    {0x96,0x0C}, {0x97,0x05}, {0x9A,0x14}, {0x9C,0x3F}, {0xA5,0x19},
    {0xCC,0x19}, {0xCD,0x0B}, {0xCE,0x13}, {0xCF,0x64}, {0xD0,0x21},
    // BANK 1
    {0xEF,0x01}, {0x02,0x0F}, {0x03,0x10}, {0x04,0x02}, {0x25,0x01},
    {0x27,0x39}, {0x28,0x7F}, {0x29,0x08}, {0x3E,0xFF}, {0x5E,0x3D},
    {0x65,0x96}, {0x67,0x97}, {0x69,0xCD}, {0x6A,0x01}, {0x6D,0x2C},
    {0x6E,0x01}, {0x72,0x01}, {0x73,0x35}, {0x77,0x01}, {0xEF,0x00},
};
//===========================================================
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
	switch(GPIO_Pin)
	{
	}
}
//============================================================
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
	if(huart == &huart2)
	{
	}
}
//============================================================
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{

}
//============================================================
int main()
{
	HAL_Init();
	HAL_MspInit(); // Initialisation des Broches
	int s = 0;
	red_led(0);

	huart2.Instance          = USART2;
	huart2.Init.BaudRate     = 115200;
	huart2.Init.WordLength   = UART_WORDLENGTH_8B;
	huart2.Init.StopBits     = UART_STOPBITS_1;
	huart2.Init.Parity       = UART_PARITY_NONE;
	HAL_UART_Init(&huart2);

	uint32_t prescalerValue;
	prescalerValue = (uint32_t) SystemCoreClock;
	htim5.Instance = TIM5;
	htim5.Init.Period =   84000;
	htim5.Init.Prescaler = 4000;
	HAL_TIM_Base_Init(&htim5);

	hi2c1.Instance = I2C1;
	hi2c1.Init.ClockSpeed = 400000;
	HAL_I2C_Init(&hi2c1);

	//huart2.Instance->DR = 'a';
	//uart_printf(&huart2,"hello\n\r");

	uint8_t buff[10];
	int16_t gesture_data;
	 for(uint8_t i = 0; i < INIT_REG_ARRAY_SIZE; i++)
	 {
		 buff[0]=initRegisterArray[i][0];buff[1]=initRegisterArray[i][1];
		 HAL_I2C_Master_Transmit_IT(&hi2c1, 0x73, buff, 2, 0);

	 }
	 char str[10];
	while(1)
	{

			buff[0]=0x44;
			HAL_I2C_Master_Transmit_IT(&hi2c1, 0x73, buff, 1, 0);
			HAL_I2C_Master_Receive_IT(&hi2c1, 0x73, buff, 1, 0);
			s = buff[0]<<8;
			buff[0]=0x43;
			HAL_I2C_Master_Transmit_IT(&hi2c1, 0x73, buff, 1, 0);
			HAL_I2C_Master_Receive_IT(&hi2c1, 0x73 , buff, 1, 0);
			s += buff[0] ;
			sprintf(str,"%d",s);
			if(s){
				HAL_UART_Transmit(&huart2, (uint8_t *)str, strlen(str));
				//uart_printf(&huart2,"%d\r\n",s);
			}
			gesture_data = ((uint16_t)buff[0] << 8) | buff[1];


			HAL_Delay(10);

	}
	return 0;
}
//============================================================

