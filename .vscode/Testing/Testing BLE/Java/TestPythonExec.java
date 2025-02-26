package Java;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

public class TestPythonExec {

    public static void main(String[] args) throws IOException {
        Runtime.getRuntime().exec("python \"C:/Users/marks/OneDrive/Documents/Code/PICO/Example VS Code Extension/KalmanPractice/LearningForRobbit/.vscode/Testing/Testing BLE/Python/Known.py\"");
    
        //String command = "python C:\\Users\\marks\\OneDrive\\Documents\\Code\\PICO\\Example VS Code Extension\\KalmanPractice\\LearningForRobbit\\.vscode\\Testing\\Testing BLE\\Python\\Known.py";
        //Process p = Runtime.getRuntime().exec(command);
        
        /*
        File file = new File(("C:/Users/marks/OneDrive/Documents/Code/PICO/Example VS Code Extension/KalmanPractice/LearningForRobbit/.vscode/Testing/Testing BLE/Python/Known.py"));

        List<String> list = new ArrayList<String>();
        list.add("python.exe");
        String absPath = file.getAbsolutePath();

        System.out.println("absPath>>"+absPath);

        list.add(absPath);
        ProcessBuilder pb = new ProcessBuilder(list);
        Process process = pb.start();

        InputStream inputStream = process.getInputStream();
        byte[] b = new byte[1024 * 1024];// {(byte) 1024};
        while (inputStream.read(b) > 0) {
            System.out.println("b.length>>"+new String(b));
        }
        

        try {
            process.waitFor();
        } catch(InterruptedException ie) {
            ie.printStackTrace();
        }  
        System.out.println("exitValue()>>"+process.exitValue());    //Should return 0 on successful execution*/
    }
}