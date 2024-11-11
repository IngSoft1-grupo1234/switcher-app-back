SHAPE_TYPES = {

                (2,2,0) :   {   
                                'SHAPE_1_A' : lambda row, col : [(row, col), (row+1,col), (row+2,col), (row+1,col+1), (row+1,col+2)],
                                'SHAPE_1_B' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row+1,col+1), (row+2,col+1)],
                                'SHAPE_4_A' : lambda row, col : [(row, col), (row+1,col), (row+1,col+1), (row+2,col+1), (row+2,col+2)],
                                'SHAPE_4_C' : lambda row, col : [(row, col), (row,col+1), (row+1,col+1), (row+1,col+2), (row+2,col+2)],
                                'SHAPE_6_A' : lambda row, col : [(row, col), (row+1,col), (row+2,col), (row+2,col+1), (row+2,col+2)],
                                'SHAPE_6_B' : lambda row, col : [(row, col), (row+1,col), (row+2,col), (row,col+1), (row,col+2)],
                                'SHAPE_6_C' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row+1,col+2), (row+2,col+2)],
                                'SHAPE_9_D' : lambda row, col : [(row, col), (row,col+1), (row+1,col+1), (row+1,col+2), (row+2,col+1)],
                                'SHAPE_10_B' : lambda row, col : [(row, col), (row,col+1), (row+1,col+1), (row+2,col+1), (row+2,col+2)],
                                'SHAPE_11_A' : lambda row, col : [(row, col), (row+1,col), (row+1,col+1), (row+2,col+1), (row+1,col+2)],
                                'SHAPE_12_A' : lambda row, col : [(row, col), (row+1,col), (row+1,col+1), (row+1,col+2), (row+2,col+2)]
                            },


                (1,2,1) :   {   
                                'SHAPE_1_C' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row-1,col+2), (row+1,col+2)],
                                'SHAPE_4_B' : lambda row, col : [(row, col), (row+1,col), (row,col+1), (row-1,col+1), (row-1,col+2)],
                                'SHAPE_9_A' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row-1,col+2), (row+1,col+1)],
                                'SHAPE_9_B' : lambda row, col : [(row, col), (row,col+1), (row+1,col+1), (row-1,col+1), (row+1,col+2)],
                                'SHAPE_9_C' : lambda row, col : [(row, col), (row+1,col), (row,col+1), (row,col+2), (row-1,col+1)],
                                'SHAPE_10_A' : lambda row, col : [(row, col), (row+1,col), (row,col+1), (row,col+2), (row-1,col+2)],
                                'SHAPE_11_B' : lambda row, col : [(row, col), (row,col+1), (row+1,col+1), (row-1,col+1), (row-1,col+2)],
                                'SHAPE_11_C' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row+1,col+2), (row-1,col+1)],
                                'SHAPE_17' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row+1,col+1), (row-1,col+1)]
                            },


                (0,2,2) :   {   
                                'SHAPE_1_D' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row-1,col+1), (row-2,col+1)],
                                'SHAPE_2_D' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row-1,col+1), (row-2,col+1)],
                                'SHAPE_4_D' : lambda row, col : [(row, col), (row,col+1), (row-1,col+1), (row-1,col+2), (row-2,col+2)],
                                'SHAPE_6_D' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row-1,col+2), (row-2,col+2)],
                                'SHAPE_11_D' : lambda row, col : [(row, col), (row,col+1), (row-1,col+1), (row-2,col+1), (row-1,col+2)],
                                'SHAPE_12_B' : lambda row, col : [(row, col), (row,col+1), (row-1,col+1), (row-2,col+1), (row-2,col+2)]
                            },
                

                (1,3,0) :   {
                                'SHAPE_2_A' : lambda row, col : [(row, col), (row,col+1), (row+1,col+1), (row+1,col+2), (row+1,col+3)],
                                'SHAPE_2_C' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row+1,col+2), (row+1,col+3)],
                                'SHAPE_7_A' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row,col+3), (row+1,col+3)],
                                'SHAPE_7_C' : lambda row, col : [(row, col), (row+1,col), (row+1,col+1), (row+1,col+2), (row+1,col+3)],
                                'SHAPE_8_C' : lambda row, col : [(row, col), (row+1,col), (row,col+1), (row,col+2), (row,col+3)],
                                'SHAPE_13_A' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row,col+3), (row+1,col+2)],
                                'SHAPE_14_C' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row,col+3), (row+1,col+1)]
                            },


                (2,1,1) :   {   
                                'SHAPE_2_B' : lambda row, col : [(row, col), (row+1,col), (row+2,col), (row,col+1), (row-1,col+1)],
                                'SHAPE_14_D' : lambda row, col : [(row, col), (row,col+1), (row+1,col+1), (row+2,col+1), (row-1,col+1)]
                            },


                (1,1,2) :   {   
                                'SHAPE_13_B' : lambda row, col : [(row, col), (row,col+1), (row+1,col+1), (row-1,col+1), (row-2,col+1)]
                            },


                (0,3,1) :   {   
                                'SHAPE_3_A' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row-1,col+2), (row-1,col+3)],
                                'SHAPE_3_C' : lambda row, col : [(row, col), (row,col+1), (row-1,col+1), (row-1,col+2), (row-1,col+3)],
                                'SHAPE_8_A' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row,col+3), (row-1,col+3)],
                                'SHAPE_13_C' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row,col+3), (row-1,col+1)],
                                'SHAPE_14_A' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row,col+3), (row-1,col+2)]
                            },

                            
                (3,1,0) :   {   
                                'SHAPE_3_B' : lambda row, col : [(row, col), (row+1,col), (row+2,col), (row+2,col+1), (row+3,col+1)],
                                'SHAPE_3_D' : lambda row, col : [(row, col), (row+1,col), (row+1,col+1), (row+2,col+1), (row+3,col+1)],
                                'SHAPE_7_D' : lambda row, col : [(row, col), (row+1,col), (row+2,col), (row+3,col), (row,col+1)],
                                'SHAPE_8_B' : lambda row, col : [(row, col), (row+1,col), (row+2,col), (row+3,col), (row+3,col+1)],
                                'SHAPE_8_D' : lambda row, col : [(row, col), (row,col+1), (row+1,col+1), (row+2,col+1), (row+3,col+1)],
                                'SHAPE_13_D' : lambda row, col : [(row, col), (row+1,col), (row+2,col), (row+3,col), (row+1,col+1)],
                                'SHAPE_14_B' : lambda row, col : [(row, col), (row+1,col), (row+2,col), (row+3,col), (row+2,col+1)]
                            },


                (0,4,0) :   {   
                                'SHAPE_5_A' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row,col+3), (row,col+4)],
                            },


                (4,0,0) :   {   
                                'SHAPE_5_B' : lambda row, col : [(row, col), (row+1,col), (row+2,col), (row+3,col), (row+4,col)]
                            },


                (0,1,3) :   {
                                'SHAPE_7_B' : lambda row, col : [(row, col), (row,col+1), (row-1,col+1), (row-2,col+1), (row-3,col+1)]
                            },


                (0,2,1) :   {   
                                'SHAPE_15_A' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row-1,col+1), (row-1,col+2)],
                                'SHAPE_19_A' : lambda row, col : [(row, col), (row,col+1), (row-1,col+1), (row-1,col+2)],
                                'SHAPE_22_A' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row-1,col+1)],
                                'SHAPE_25_A' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row-1,col+2)]
                            },


                (2,1,0) :   {   
                                'SHAPE_15_B' : lambda row, col : [(row, col), (row+1,col), (row+2,col), (row+1,col+1), (row+2,col+1)],
                                'SHAPE_15_D' : lambda row, col : [(row, col), (row+1,col), (row,col+1), (row+1,col+1), (row+2,col+1)],
                                'SHAPE_16_B' : lambda row, col : [(row, col), (row+1,col), (row+2,col), (row,col+1), (row+2,col+1)],
                                'SHAPE_16_D' : lambda row, col : [(row, col), (row,col+1), (row+1,col+1), (row+2,col+1), (row+2,col)],
                                'SHAPE_18_D' : lambda row, col : [(row, col), (row+1,col), (row+2,col), (row,col+1), (row+1,col+1)],
                                'SHAPE_19_B' : lambda row, col : [(row, col), (row+1,col), (row+1,col+1), (row+2,col+1)],
                                'SHAPE_22_B' : lambda row, col : [(row, col), (row+1,col), (row+2,col), (row+1,col+1)],
                                'SHAPE_23_D' : lambda row, col : [(row, col), (row+1,col), (row+2,col), (row,col+1)],
                                'SHAPE_25_B' : lambda row, col : [(row, col), (row+1,col), (row+2,col), (row+2,col+1)],
                                'SHAPE_25_D' : lambda row, col : [(row, col), (row,col+1), (row+1,col+1), (row+2,col+1)]
                            },
                
                (1,2,0) :   {
                                'SHAPE_15_C' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row+1,col), (row+1,col+1)],
                                'SHAPE_16_A' : lambda row, col : [(row, col), (row+1,col), (row+1,col+1), (row+1,col+2), (row,col+2)],
                                'SHAPE_16_C' : lambda row, col : [(row, col), (row+1,col), (row,col+1), (row,col+2), (row+1,col+2)],
                                'SHAPE_18_A' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row+1,col+1), (row+1,col+2)],
                                'SHAPE_18_C' : lambda row, col : [(row, col), (row,col+1), (row+1,col), (row+1,col+1), (row+1,col+2)],
                                'SHAPE_21_A' : lambda row, col : [(row, col), (row,col+1), (row+1,col+1), (row+1,col+2)],
                                'SHAPE_22_C' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row+1,col+1)],
                                'SHAPE_23_A' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row+1,col+2)],
                                'SHAPE_23_C' : lambda row, col : [(row, col), (row+1,col), (row+1,col+1), (row+1,col+2)],
                                'SHAPE_25_C' : lambda row, col : [(row, col), (row+1,col), (row,col+1), (row,col+2)]
                            },


                (1,1,1) :   {   
                                'SHAPE_18_B' : lambda row, col : [(row, col), (row+1,col), (row,col+1), (row+1,col+1), (row-1,col+1)],
                                'SHAPE_21_B' : lambda row, col : [(row, col), (row+1,col), (row,col+1), (row-1,col+1)],
                                'SHAPE_22_D' : lambda row, col : [(row, col), (row,col+1), (row+1,col+1), (row-1,col+1)]
                            },


                (1,1,0) :   {   
                                'SHAPE_20' : lambda row, col : [(row, col), (row+1,col), (row,col+1), (row+1,col+1)]
                            },


                (0,1,2) :   {   
                                'SHAPE_23_B' : lambda row, col : [(row, col), (row,col+1), (row-1,col+1), (row-2,col+1)],
                            },


                (0,3,0) :   {   
                                'SHAPE_24_A' : lambda row, col : [(row, col), (row,col+1), (row,col+2), (row,col+3)]
                            },


                (3,0,0) :   {   
                                'SHAPE_24_B' : lambda row, col : [(row, col), (row+1,col), (row+2,col), (row+3,col)]
                            },
}
