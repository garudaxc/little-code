

def ReadCSVFile(filename):

    shaders = set()
    unique_shader_type = dict()

    # parse csv file
    with open(filename, 'r') as f:
        # skip header
        f.readline()        

        num_line = 0
        while True:
            line = f.readline()
            if not line:
                break

            # parse shader name
            tokens = line.split('\"')
            vertex_shader_info = tokens[5]
            fragment_shader_info = tokens[11]
            
            try:
                if vertex_shader_info != '':
                    vertex_shader, vertex_shader_type = tuple(vertex_shader_info.split(',')[0: 2])
                    shaders.add(vertex_shader)

                    if vertex_shader_type not in unique_shader_type:
                        unique_shader_type[vertex_shader_type] = 1
                    else:
                        unique_shader_type[vertex_shader_type] += 1

                if fragment_shader_info != '':
                    fragment_shader, fragment_shader_type = tuple(fragment_shader_info.split(',')[0: 2])
                    shaders.add(fragment_shader)
                    if fragment_shader_type not in unique_shader_type:
                        unique_shader_type[fragment_shader_type] = 1
                    else:
                        unique_shader_type[fragment_shader_type] += 1
            
            except:
                print(num_line)
                print("vertex_shader_info", vertex_shader_info)
                print("fragment_shader_info", fragment_shader_info)
                # print(vertex_shader_info.split(','))
                break


            num_line += 1

    # for shader in shaders:
    #     print(shader)
    print("number of lines : ", num_line)
    print("number of shaders : ", len(shaders))
    print("number of unique shader types : ", len(unique_shader_type))

    unique_shader_type_list = list(unique_shader_type.keys())
    unique_shader_type_list.sort()
    for shader_type in unique_shader_type_list:
        print(shader_type, unique_shader_type[shader_type])


def Main():

    file = r"D:\ka1_client\client\trunk\BeyondStar\Build\Android\PipelineCaches\BeyondStar_GLSL_ES3_1_ANDROID.stablepc.csv"
    ReadCSVFile(file)
    

if __name__ == '__main__':
    Main() 